<?php
/**
 * Kontaktformular-Handler (Apache + PHP >= 7.2, z. B. IONOS, DomainFactory, Strato)
 *
 * - nimmt die Formulardaten per POST entgegen und verschickt sie per E-Mail
 * - Schutz: Honeypot-Feld, vom Server signierter Zeitstempel (api/token.php) mit Mindest-/Höchstalter,
 *   Origin-/Referer-Prüfung, Rate-Limits (pro IP und insgesamt), Header-Injection-Schutz,
 *   Längenbegrenzung, Pflicht-Einwilligung
 * - speichert nichts auf dem Server (außer einem anonymen IP-Hash-Zeitstempel im Temp-Verzeichnis)
 *
 * KONFIGURATION: content/config.json (Empfänger, Absender, Themen) – nicht diese Datei ändern.
 */

// Empfänger, Absender, Themen und erlaubte Hosts kommen aus content/config.json (build.py erzeugt api/config.php).
// Absender: MUSS eine Adresse der eigenen Domain sein (viele Hoster verwerfen sonst die Mail).
// Mindestdauer (Sekunden) zwischen Seitenaufruf und Absenden (Bot-Schutz)
const CONTACT_MIN_SECONDS = 4;
// Falls der Mailversand bei IONOS fehlschlägt: auf false setzen (dann wird der Absender nicht zusätzlich als Envelope-From gesetzt)
const CONTACT_USE_ENVELOPE_FROM = true;

// Rate-Limits: je IP und insgesamt (Anfragen pro Stunde) – verhindert Postfach-Flutung
const CONTACT_LIMIT_PER_IP_HOUR = 5;
const CONTACT_LIMIT_TOTAL_HOUR  = 40;
// Signierter Zeitstempel: so lange gültig (Sekunden)
const CONTACT_MAX_SECONDS = 7200;

require __DIR__ . '/common.php';

header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');

$accept   = isset($_SERVER['HTTP_ACCEPT']) ? $_SERVER['HTTP_ACCEPT'] : '';
$wantJson = strpos($accept, 'application/json') !== false;
$lang     = (isset($_POST['lang']) && is_string($_POST['lang']) && isset(MSG[$_POST['lang']])) ? $_POST['lang'] : DEFAULT_LANG;

function respond($ok, $key, $code, $wantJson, $lang)
{
    $text = MSG[$lang][$key];
    http_response_code($code);
    if ($wantJson) {
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode(array('ok' => $ok, 'message' => $text));
        exit;
    }
    header('Content-Type: text/html; charset=utf-8');
    $color = $ok ? '#1d8a3d' : '#d70015';
    echo '<!doctype html><html lang="' . $lang . '"><head><meta charset="utf-8">'
       . '<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">'
       . '<title>' . htmlspecialchars(SITE_NAME, ENT_QUOTES, 'UTF-8') . '</title></head>'
       . '<body style="font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Arial,sans-serif;max-width:560px;margin:15vh auto;padding:0 24px;text-align:center;color:#1d1d1f">'
       . '<p style="font-size:1.25rem;color:' . $color . '">' . htmlspecialchars($text, ENT_QUOTES, 'UTF-8') . '</p>'
       . '<p><a href="/" style="color:#0066cc">' . htmlspecialchars(MSG[$lang]['back'], ENT_QUOTES, 'UTF-8') . '</a></p>'
       . '</body></html>';
    exit;
}

function clean($value, $max)
{
    $value = is_string($value) ? $value : '';
    $value = preg_replace('/[^\P{C}\n\t]+/u', '', $value); // Steuerzeichen entfernen
    if ($value === null) { // ungültiges UTF-8
        return '';
    }
    $value = trim($value);
    return function_exists('mb_substr') ? mb_substr($value, 0, $max, 'UTF-8') : substr($value, 0, $max);
}

function one_line($value)
{
    return trim(preg_replace('/[\r\n\t]+/', ' ', $value));
}

if (!isset($_SERVER['REQUEST_METHOD']) || $_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Allow: POST');
    respond(false, 'fail', 405, $wantJson, $lang);
}

// Honeypot: Bots füllen das versteckte Feld aus -> stillschweigend "erfolgreich" beenden
if (!empty($_POST['website'])) {
    respond(true, 'ok', 200, $wantJson, $lang);
}

// Anfrage muss von der eigenen Website kommen (Origin/Referer), falls der Browser sie mitsendet
if (!origin_ok()) {
    respond(false, 'invalid', 403, $wantJson, $lang);
}

// Signierter Zeitstempel (von api/token.php): Pflicht, Mindest-Ausfüllzeit und Höchstalter
$tsRaw  = (isset($_POST['ts']) && is_string($_POST['ts'])) ? $_POST['ts'] : '';
$sigRaw = (isset($_POST['sig']) && is_string($_POST['sig'])) ? $_POST['sig'] : '';
if ($tsRaw === '' || !ctype_digit($tsRaw) || $sigRaw === '' || !hash_equals(form_sign($tsRaw), $sigRaw)) {
    respond(false, 'slow', 429, $wantJson, $lang);
}
$age = time() - (int) $tsRaw;
if ($age < CONTACT_MIN_SECONDS || $age > CONTACT_MAX_SECONDS) {
    respond(false, 'slow', 429, $wantJson, $lang);
}

// Rate-Limit: höchstens eine Anfrage je IP alle 30 Sekunden
$ip   = isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : 'unknown';
$lock = rtrim(sys_get_temp_dir(), '/\\') . '/site_contact_' . hash('sha256', __DIR__ . '|' . $ip);
if (is_file($lock) && (time() - (int) @filemtime($lock)) < 30) {
    respond(false, 'slow', 429, $wantJson, $lang);
}

$name    = one_line(clean(isset($_POST['name']) ? $_POST['name'] : '', 120));
$email   = one_line(clean(isset($_POST['email']) ? $_POST['email'] : '', 160));
$company = one_line(clean(isset($_POST['company']) ? $_POST['company'] : '', 160));
$phone   = one_line(clean(isset($_POST['phone']) ? $_POST['phone'] : '', 60));
$message = clean(isset($_POST['message']) ? $_POST['message'] : '', 5000);
$topicRaw = (isset($_POST['topic']) && is_string($_POST['topic'])) ? $_POST['topic'] : '';
$topicKeys = array_keys(TOPICS);
$topicKey = array_key_exists($topicRaw, TOPICS) ? $topicRaw : end($topicKeys);
$consent = !empty($_POST['consent']);

if ($name === '' || $message === '' || !$consent || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    respond(false, 'invalid', 400, $wantJson, $lang);
}

// Stündliche Limits (erst nach erfolgreicher Prüfung zählen)
if (!rate_hit('ip|' . $ip, CONTACT_LIMIT_PER_IP_HOUR, 3600) || !rate_hit('total', CONTACT_LIMIT_TOTAL_HOUR, 3600)) {
    respond(false, 'slow', 429, $wantJson, $lang);
}

$topic   = isset(TOPICS[$topicKey][DEFAULT_LANG]) ? TOPICS[$topicKey][DEFAULT_LANG] : (string) $topicKey;
$subject = 'Neue Anfrage über ' . SITE_NAME . ': ' . $topic;
$body    = "Neue Anfrage über das Kontaktformular auf " . SITE_NAME . "\n"
         . "------------------------------------------------\n"
         . "Thema:       " . $topic . "\n"
         . "Name:        " . $name . "\n"
         . "E-Mail:      " . $email . "\n"
         . "Unternehmen: " . ($company !== '' ? $company : '-') . "\n"
         . "Telefon:     " . ($phone !== '' ? $phone : '-') . "\n"
         . "Sprache:     " . strtoupper($lang) . "\n"
         . "Einwilligung zur Datenverarbeitung: ja (" . date('Y-m-d H:i:s') . ")\n"
         . "------------------------------------------------\n\n"
         . $message . "\n";

$headers = array(
    'From: ' . SITE_NAME . ' Website <' . CONTACT_FROM . '>',
    'Reply-To: ' . $email, // $email ist validiert und einzeilig -> kein Header-Injection-Risiko
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
    'X-Mailer: website-contact-form',
);

$encodedSubject = '=?UTF-8?B?' . base64_encode($subject) . '?=';
if (CONTACT_USE_ENVELOPE_FROM) {
    $sent = @mail(CONTACT_TO, $encodedSubject, $body, implode("\r\n", $headers), '-f' . CONTACT_FROM);
} else {
    $sent = @mail(CONTACT_TO, $encodedSubject, $body, implode("\r\n", $headers));
}

if (!$sent) {
    respond(false, 'fail', 500, $wantJson, $lang);
}

@touch($lock);
respond(true, 'ok', 200, $wantJson, $lang);
