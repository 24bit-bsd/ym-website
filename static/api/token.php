<?php
/**
 * Liefert einen signierten Zeitstempel für das Kontaktformular (Bot-Schutz).
 * contact.php prüft Signatur und Mindest-/Höchstalter; ein selbst gesetzter Zeitstempel wird abgelehnt.
 */
require __DIR__ . '/common.php';

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');

if (!origin_ok()) {
    http_response_code(403);
    echo json_encode(array('ok' => false));
    exit;
}

$ts = time();
echo json_encode(array('ts' => $ts, 'sig' => form_sign($ts)));
