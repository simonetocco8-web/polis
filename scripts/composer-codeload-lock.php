<?php

// Create an alternate, temporary Composer manifest for restricted GitHub egress.
$target = $argv[1] ?? '';
if ($target === '' || ! is_dir($target)) {
    fwrite(STDERR, "Fornire la directory temporanea per il manifest Composer.\n");
    exit(2);
}

$lock = json_decode(file_get_contents('composer.lock'), true, 64, JSON_THROW_ON_ERROR);
foreach (['packages', 'packages-dev'] as $group) {
    foreach ($lock[$group] as &$package) {
        $dist = $package['dist'] ?? [];
        $url = $dist['url'] ?? '';
        if (preg_match('~\Ahttps://api\.github\.com/repos/([a-z0-9_.-]+/[a-z0-9_.-]+)/zipball/([a-f0-9]{40})\z~i', $url, $parts)
            && $parts[2] === ($dist['reference'] ?? null)) {
            $package['dist']['url'] = "https://codeload.github.com/{$parts[1]}/zip/{$parts[2]}";
        }
    }
    unset($package);
}

if (! copy('composer.json', $target.'/composer.json')
    || file_put_contents($target.'/composer.lock', json_encode($lock, JSON_THROW_ON_ERROR)) === false) {
    fwrite(STDERR, "Impossibile salvare il manifest temporaneo.\n");
    exit(1);
}
