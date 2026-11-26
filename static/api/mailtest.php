<?php
// TEMPORÄR zur Fehlersuche beim Mailversand – wird nach dem Test wieder entfernt.
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
if (!isset($_GET['k']) || !hash_equals('7603a8cc430a5bbd42f19164e0b2ba8540c888474a22563d311bf31e3578beee', hash('sha256', (string) $_GET['k']))) { http_response_code(404); exit; }
require __DIR__ . '/config.php';
$variant = isset($_GET['v']) ? (string) $_GET['v'] : 'a';
$headers = 'From: ' . CONTACT_FROM . "\r\nContent-Type: text/plain; charset=UTF-8";
if ($variant === 'b') { $headers = ''; }                    // ohne eigene Header
if ($variant === 'c') { $headers = 'From: ' . SITE_NAME . ' Website <' . CONTACT_FROM . '>'; }
$res = array(
  'php' => PHP_VERSION, 'variant' => $variant, 'to' => CONTACT_TO, 'from' => CONTACT_FROM,
  'sendmail_path' => ini_get('sendmail_path'), 'sendmail_from' => ini_get('sendmail_from'),
  'disabled' => ini_get('disable_functions'), 'mail_exists' => function_exists('mail'),
);
@error_clear_last();
$ok = @mail(CONTACT_TO, 'TEST Mailversand ' . $variant . ' (bitte ignorieren)', "Diagnose-Mail vom Staging, Variante " . $variant . ".\n", $headers);
$res['mail_result'] = $ok;
$res['error'] = error_get_last();
echo json_encode($res, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
