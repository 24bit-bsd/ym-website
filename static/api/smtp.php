<?php
/**
 * Minimaler SMTP-Versand mit Anmeldung (für Hoster, bei denen PHP mail() nicht funktioniert, z. B. IONOS).
 * Zugangsdaten stehen NICHT im Repository: api/smtp-config.php wird beim Deployment aus den GitHub-Secrets
 * SMTP_USER und SMTP_PASSWORD erzeugt (siehe .github/workflows/deploy.yml).
 * Gibt bei direktem Aufruf nichts aus.
 */

function smtp_read($fp)
{
    $data = '';
    while (($line = fgets($fp, 1024)) !== false) {
        $data .= $line;
        if (strlen($line) < 4 || $line[3] !== '-') {
            break;
        }
    }
    return $data;
}

function smtp_cmd($fp, $line, $expect)
{
    if ($line !== null) {
        fwrite($fp, $line . "\r\n");
    }
    $reply = smtp_read($fp);
    return $reply !== '' && in_array((int) substr($reply, 0, 3), (array) $expect, true);
}

/** Verschickt eine Textmail per SMTP. Gibt true bei Erfolg zurück. */
function smtp_send(array $cfg, $from, $fromName, $to, $replyTo, $subject, $body)
{
    $secure = isset($cfg['secure']) ? $cfg['secure'] : 'starttls'; // starttls | ssl | none
    $host = $cfg['host'];
    $port = (int) $cfg['port'];
    $target = ($secure === 'ssl' ? 'ssl://' : 'tcp://') . $host . ':' . $port;
    $fp = @stream_socket_client($target, $errno, $errstr, 15);
    if (!$fp) {
        return false;
    }
    stream_set_timeout($fp, 20);
    $ehlo = 'EHLO ' . (preg_match('/^[A-Za-z0-9.-]+$/', (string) gethostname()) ? gethostname() : 'localhost');
    $ok = smtp_cmd($fp, null, 220) && smtp_cmd($fp, $ehlo, 250);
    if ($ok && $secure === 'starttls') {
        $ok = smtp_cmd($fp, 'STARTTLS', 220)
            && @stream_socket_enable_crypto($fp, true, STREAM_CRYPTO_METHOD_TLS_CLIENT)
            && smtp_cmd($fp, $ehlo, 250);
    }
    if ($ok && $cfg['user'] !== '') {
        $ok = smtp_cmd($fp, 'AUTH LOGIN', 334)
            && smtp_cmd($fp, base64_encode($cfg['user']), 334)
            && smtp_cmd($fp, base64_encode($cfg['pass']), 235);
    }
    $ok = $ok && smtp_cmd($fp, 'MAIL FROM:<' . $from . '>', 250) && smtp_cmd($fp, 'RCPT TO:<' . $to . '>', array(250, 251)) && smtp_cmd($fp, 'DATA', 354);
    if ($ok) {
        $headers = array(
            'Date: ' . date('r'),
            'From: =?UTF-8?B?' . base64_encode($fromName) . '?= <' . $from . '>',
            'To: <' . $to . '>',
            'Reply-To: <' . $replyTo . '>',
            'Subject: =?UTF-8?B?' . base64_encode($subject) . '?=',
            'Message-ID: <' . bin2hex(random_bytes(8)) . '@' . preg_replace('/^.*@/', '', $from) . '>',
            'MIME-Version: 1.0',
            'Content-Type: text/plain; charset=UTF-8',
            'Content-Transfer-Encoding: 8bit',
            'X-Mailer: website-contact-form',
        );
        $text = preg_replace('/\r\n|\r|\n/', "\r\n", $body);
        $text = preg_replace('/^\./m', '..', $text); // Dot-Stuffing
        fwrite($fp, implode("\r\n", $headers) . "\r\n\r\n" . $text . "\r\n.\r\n");
        $ok = smtp_cmd($fp, null, 250);
    }
    if ($fp) {
        @fwrite($fp, "QUIT\r\n");
        @fclose($fp);
    }
    return $ok;
}
