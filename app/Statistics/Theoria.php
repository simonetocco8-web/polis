<?php

namespace App\Statistics;

use RuntimeException;

final class Theoria
{
    public const HASH = '6c1a1c64df767d2d456ef8ceb6269b5d54a4db776da8c602fa79b78f08b66b2f';

    public function load(): array
    {
        $dir = config('polis.content').'/statistics/';
        $raw = file_get_contents($dir.'theoria.json');
        $checksum = file_get_contents($dir.'theoria.sha256');
        if ($raw === false || $checksum === false || trim($checksum) !== self::HASH
            || ! hash_equals(self::HASH, hash('sha256', $raw))) {
            throw new RuntimeException('Fascicolo Theoria non autorizzato.');
        }
        $data = json_decode($raw, true, 32, JSON_THROW_ON_ERROR);
        if ($data['version'] !== 'theoria-1.0' || $data['mode'] !== 'offline-public-fixture'
            || $data['source_sha256'] !== hash_file('sha256', $dir.'archon.json')
            || array_column($data['cases'], 'period') !== [1, 2, 3, 4]) {
            throw new RuntimeException('Provenienza Theoria incoerente.');
        }

        return $data;
    }
}
