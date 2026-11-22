<?php

if (! preg_match('/\A[0-9a-f]{40}\z/', $argv[1] ?? '')) {
    fwrite(STDERR, "Fornire lo SHA Git della revisione di riferimento.\n");
    exit(2);
}

$manifest = 'content/metadata/documents.json';
$git = static function (array $arguments): ?string {
    $process = proc_open(['git', ...$arguments], [0 => ['file', '/dev/null', 'r'], 1 => ['pipe', 'w'], 2 => ['file', '/dev/null', 'w']], $pipes);
    if (! is_resource($process)) {
        throw new RuntimeException('Git non disponibile');
    }
    $output = stream_get_contents($pipes[1]);
    fclose($pipes[1]);

    return proc_close($process) === 0 && $output !== false ? $output : null;
};

$base = $argv[1];
if ($git(['rev-parse', '--verify', $base.'^{commit}']) === null) {
    fwrite(STDERR, "Revisione Git di riferimento non disponibile.\n");
    exit(2);
}

$files = $git(['ls-tree', '--name-only', $base, '--', $manifest]);
if ($files === null) {
    throw new RuntimeException('Impossibile ispezionare il manifest storico');
}
if ($files === '') {
    exit(0);
}

$normalize = static function (mixed $value) use (&$normalize): mixed {
    if (is_array($value)) {
        if (! array_is_list($value)) {
            ksort($value);
        }
        foreach ($value as $key => $item) {
            $value[$key] = $normalize($item);
        }
    }

    return $value;
};

$previous = json_decode($git(['show', $base.':'.$manifest]) ?? '', true, 32, JSON_THROW_ON_ERROR);
$current = json_decode(file_get_contents($manifest), true, 32, JSON_THROW_ON_ERROR);
foreach ($previous as $language => $documents) {
    foreach ($documents as $id => $document) {
        foreach ($document['versions'] as $version => $metadata) {
            if ($normalize($current[$language][$id]['versions'][$version] ?? null) !== $normalize($metadata)) {
                fwrite(STDERR, "Versione pubblicata modificata o rimossa: {$language}/{$id}/{$version}\n");
                exit(1);
            }
        }
    }
}
echo "Metadati delle versioni storiche preservati.\n";
