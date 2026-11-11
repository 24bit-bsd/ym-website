<?php
/**
 * Gemeinsame Helfer für api/contact.php und api/token.php (PHP >= 7.2)
 * Gibt bei direktem Aufruf nichts aus.
 */

require_once __DIR__ . '/config.php'; // ALLOWED_HOSTS u. a. (aus content/config.json erzeugt)

/** Geheimer Schlüssel für die Signatur; wird einmalig zufällig erzeugt und liegt nicht im Repository. */
function form_secret()
{
    $path = rtrim(sys_get_temp_dir(), '/\\') . '/site_form_secret_' . substr(hash('sha256', __DIR__), 0, 12);
    $s = is_file($path) ? @file_get_contents($path) : false;
    if (is_string($s) && strlen(trim($s)) >= 32) {
        return trim($s);
    }
    $s = bin2hex(random_bytes(32));
    if (@file_put_contents($path, $s, LOCK_EX) === false) {
        // Notlösung, falls das Temp-Verzeichnis nicht beschreibbar ist: stabiler, serverspezifischer Schlüssel
        return hash('sha256', __FILE__ . '|' . php_uname() . '|' . (string) @filemtime(__FILE__));
    }
    @chmod($path, 0600);
    return $s;
}

function form_sign($ts)
{
    return hash_hmac('sha256', (string) $ts, form_secret());
}

/** true, wenn die Anfrage nicht von einer fremden Seite kommt (fehlende Header sind erlaubt). */
function origin_ok()
{
    foreach (array('HTTP_ORIGIN', 'HTTP_REFERER') as $key) {
        if (!empty($_SERVER[$key])) {
            $host = parse_url((string) $_SERVER[$key], PHP_URL_HOST);
            return is_string($host) && in_array(strtolower($host), ALLOWED_HOSTS, true);
        }
    }
    return true;
}

/**
 * Zählt einen Treffer im Zeitfenster und liefert false, wenn das Limit erreicht ist.
 * Speicherung: Zeitstempel in einer Datei im Temp-Verzeichnis (anonym, nur Zahlen).
 */
function rate_hit($name, $limit, $window)
{
    $file = rtrim(sys_get_temp_dir(), '/\\') . '/site_rate_' . hash('sha256', $name . '|' . __DIR__);
    $fh = @fopen($file, 'c+');
    if (!$fh) {
        return true; // lieber senden als blockieren, wenn der Speicher fehlt
    }
    flock($fh, LOCK_EX);
    $raw = stream_get_contents($fh);
    $now = time();
    $hits = array();
    foreach (preg_split('/\s+/', trim((string) $raw)) as $t) {
        if ($t !== '' && ctype_digit($t) && ($now - (int) $t) < $window) {
            $hits[] = (int) $t;
        }
    }
    $ok = count($hits) < $limit;
    if ($ok) {
        $hits[] = $now;
    }
    ftruncate($fh, 0);
    rewind($fh);
    fwrite($fh, implode("\n", $hits));
    flock($fh, LOCK_UN);
    fclose($fh);
    return $ok;
}
