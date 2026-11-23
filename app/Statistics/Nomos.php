<?php

namespace App\Statistics;

use RuntimeException;

final class Nomos
{
    private const RELEASE_HASH = 'ff63f668a5f8ac0a9e7ff0de8ee09357946573d28cd84c693aea7640122dee9c';

    public function load(): array
    {
        $root = config('polis.content');
        $raw = file_get_contents($root.'/statistics/nomos.json');
        $checksum = file_get_contents($root.'/statistics/nomos.sha256');
        if ($raw === false || $checksum === false || trim($checksum) !== self::RELEASE_HASH
            || ! hash_equals(self::RELEASE_HASH, hash('sha256', $raw))) {
            throw new RuntimeException('Esportazione Nomos non riconosciuta.');
        }

        $data = json_decode($raw, true, 32, JSON_THROW_ON_ERROR);
        if ($data['version'] !== 'nomos-1.0' || $data['type'] !== 'demonstration' || $data['regime'] !== 'B'
            || $data['provenance']['constitution'] !== hash_file('sha256', $root.'/documents/it/costituzione/1.0.md')
            || ! preg_match('/^[a-f0-9]{64}$/D', $data['journal_sha256'])
            || array_column($data['scenarios'], 'id') !== ['A', 'B', 'C', 'D', 'E', 'F']
            || count($data['acts']) !== $data['metrics']['proposed']
            || $data['metrics']['upheld'] + $data['metrics']['dismissed'] > $data['metrics']['appeals']
            || $data['metrics']['applied'] > $data['metrics']['authorized']) {
            throw new RuntimeException('Struttura o provenienza Nomos incoerente.');
        }

        return $data;
    }

    public function checksum(): string
    {
        return self::RELEASE_HASH;
    }
}
