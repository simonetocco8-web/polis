<?php

namespace App\Statistics;

use RuntimeException;

final class Archon
{
    private const RELEASE_HASH = '811ec7e7346fdee95c50d55e9722db7c1f060e7c9894ad7e877aeca6325eeb45';

    public function checksum(): string
    {
        return self::RELEASE_HASH;
    }

    public function load(): array
    {
        $root = config('polis.content').'/statistics';
        $raw = file_get_contents($root.'/archon.json');
        $checksum = file_get_contents($root.'/archon.sha256');
        if ($raw === false || $checksum === false || trim($checksum) !== self::RELEASE_HASH
            || ! hash_equals(self::RELEASE_HASH, hash('sha256', $raw))) {
            throw new RuntimeException('Esportazione Archon sconosciuta.');
        }

        $data = json_decode($raw, true, 32, JSON_THROW_ON_ERROR);
        if ($data['version'] !== 'archon-1.0' || $data['mode'] !== 'offline' || $data['provider'] !== 'offline'
            || $data['model'] !== 'fixture-1.0' || $data['scenario'] !== 'B' || $data['api_calls'] !== 0
            || $data['api_cost_micro_usd'] !== 0 || $data['api_input_tokens'] !== 0 || $data['api_output_tokens'] !== 0
            || ! preg_match('/^[0-9a-f]{64}$/D', $data['nomos_sha256']) || ! preg_match('/^[0-9a-f]{64}$/D', $data['decision_sha256'])
            || array_column($data['decisions'], 'period') !== [1, 2, 3, 4]) {
            throw new RuntimeException('Provenienza o sequenza Archon incoerente.');
        }
        foreach ($data['decisions'] as $entry) {
            if ($entry['applied'] && ($entry['outcome'] !== 'PROPOSE' || $entry['court'] !== 'authorized')) {
                throw new RuntimeException('Applicazione priva di autorizzazione.');
            }
        }

        return $data;
    }
}
