<?php

namespace App\Statistics;

use RuntimeException;

final class Experimentum
{
    public const HASH = '9c040a48add77eaa5bdad1b5331b6085f022bb6ac14eb67307a2deb19b5346d0';

    public function load(): array
    {
        $dir = config('polis.content').'/statistics/';
        $raw = file_get_contents($dir.'experimentum.json');
        $checksum = file_get_contents($dir.'experimentum.sha256');
        if ($raw === false || $checksum === false || trim($checksum) !== self::HASH
            || ! hash_equals(self::HASH, hash('sha256', $raw))) {
            throw new RuntimeException('Fascicolo Experimentum non autorizzato.');
        }
        $data = json_decode($raw, true, 32, JSON_THROW_ON_ERROR);
        if ($data['version'] !== 'experimentum-1.0' || $data['mode'] !== 'offline-technical'
            || $data['protocol_sha256'] !== '448c86c5e09e4db25dba6a0d35f79fd6092bb40641e8cb96dfda1a1df085c0b7'
            || $data['state'] !== 'REPRODUCED' || $data['readiness']['state'] !== 'NOT_READY'
            || $data['api_calls'] !== 0 || count($data['replicas']) !== 3) {
            throw new RuntimeException('Provenienza Experimentum incoerente.');
        }

        return $data;
    }
}
