<?php

namespace App\Documents;

use DateTimeImmutable;
use Illuminate\Support\Facades\File;
use RuntimeException;

final class Library
{
    public function __construct(private Markdown $markdown) {}

    public function documents(?string $language = null): array
    {
        return $this->manifest()[$language ?? app()->getLocale()] ?? [];
    }

    public function entry(string $id): ?array
    {
        return $this->documents()[$id] ?? null;
    }

    public function read(string $id, ?string $version = null, ?string $language = null): ?array
    {
        $language ??= app()->getLocale();
        $document = $this->documents($language)[$id] ?? null;
        $version ??= $document['current'] ?? null;
        $metadata = $version === null ? null : ($document['versions'][$version] ?? null);

        if ($metadata === null) {
            return null;
        }

        $source = $this->verifiedSource($language, $id, $version, $metadata['sha256']);
        $structure = $metadata['structure'] ?? null;
        $articleLinkBase = $structure === null ? '' : route('constitution.version', $version, false);
        $rendered = $this->markdown->render($source, $structure, $articleLinkBase);

        return $rendered + $metadata + ['source' => $source, 'version' => $version, 'language' => $language];
    }

    public function validate(): int
    {
        $knownFiles = [];
        foreach ($this->manifest() as $language => $documents) {
            foreach ($documents as $id => $document) {
                foreach (array_keys($document['versions']) as $version) {
                    $this->read($id, $version, $language);
                    $knownFiles["{$language}/{$id}/{$version}.md"] = true;
                }
            }
        }

        foreach (File::allFiles(config('polis.content').'/documents') as $file) {
            if ($file->getExtension() === 'md' && ! isset($knownFiles[$file->getRelativePathname()])) {
                throw new RuntimeException('File Markdown assente dal manifest: '.$file->getRelativePathname());
            }
        }

        return count($knownFiles);
    }

    private function manifest(): array
    {
        $path = config('polis.content').'/metadata/documents.json';
        $raw = is_file($path) ? file_get_contents($path) : false;
        $manifest = $raw === false ? null : json_decode($raw, true, 32, JSON_THROW_ON_ERROR);
        if (! is_array($manifest) || $manifest === []) {
            throw new RuntimeException('Manifest documentale assente o non valido');
        }

        foreach ($manifest as $language => $documents) {
            if (! preg_match('/\A[a-z]{2}\z/', (string) $language) || ! is_array($documents)) {
                throw new RuntimeException('Lingua documentale non valida');
            }
            foreach ($documents as $id => $document) {
                if (! preg_match('/\A[a-z][a-z0-9-]*\z/', (string) $id) || ! is_array($document)) {
                    throw new RuntimeException('Identificativo documentale non valido');
                }
                $this->requireStrings($document, ['title', 'subtitle', 'type', 'expected_version', 'expected_date']);
                $versions = $document['versions'] ?? null;
                $current = $document['current'] ?? null;
                if (! is_array($versions) || ($versions === [] ? $current !== null : ! is_string($current) || ! isset($versions[$current]))) {
                    throw new RuntimeException("Versione corrente non valida: {$id}");
                }
                foreach ($versions as $version => $metadata) {
                    $this->validateMetadata((string) $version, $metadata, $versions, $id, $language);
                }
            }
        }

        return $manifest;
    }

    private function validateMetadata(string $version, mixed $metadata, array $versions, string $id, string $language): void
    {
        if (! preg_match('/\A\d+\.\d+(?:\.\d+)?\z/', $version) || ! is_array($metadata)) {
            throw new RuntimeException('Versione documentale non valida');
        }
        $this->requireStrings($metadata, ['date', 'author', 'status', 'sha256', 'provenance', 'changes', 'original_language']);
        $date = DateTimeImmutable::createFromFormat('!Y-m-d', $metadata['date']);
        $previous = $metadata['previous'] ?? null;
        if (! $date || $date->format('Y-m-d') !== $metadata['date']
            || ! preg_match('/\A[a-f0-9]{64}\z/', $metadata['sha256'])
            || ($previous !== null && (! is_string($previous) || ! isset($versions[$previous]) || ! version_compare($previous, $version, '<')))) {
            throw new RuntimeException("Metadati non validi per {$id} {$version}");
        }

        if (! preg_match('/\A[a-z]{2}\z/', $metadata['original_language'])) {
            throw new RuntimeException('Lingua originale non valida');
        }
        if ($metadata['original_language'] !== $language) {
            $this->requireStrings($metadata, ['translation_date', 'translator', 'translation_review']);
            $translationDate = DateTimeImmutable::createFromFormat('!Y-m-d', $metadata['translation_date']);
            if (! $translationDate || $translationDate->format('Y-m-d') !== $metadata['translation_date']) {
                throw new RuntimeException('Data di traduzione non valida');
            }
        }

        if ($id !== 'costituzione' && isset($metadata['structure'])) {
            throw new RuntimeException('La struttura di articoli è riservata alla Costituzione');
        }

        if ($id === 'costituzione') {
            $structure = $metadata['structure'] ?? null;
            if (! is_array($structure)
                || ! is_int($structure['articles'] ?? null) || $structure['articles'] < 1
                || ! is_int($structure['titles'] ?? null) || $structure['titles'] < 1
                || ($version === '1.0' && ($structure['articles'] !== 71 || $structure['titles'] !== 12))) {
                throw new RuntimeException('Requisiti della struttura costituzionale non validi');
            }
        }
    }

    /** @param list<string> $keys */
    private function requireStrings(array $data, array $keys): void
    {
        foreach ($keys as $key) {
            if (! is_string($data[$key] ?? null) || trim($data[$key]) === '') {
                throw new RuntimeException("Metadato mancante o non valido: {$key}");
            }
        }
    }

    private function verifiedSource(string $language, string $id, string $version, string $sha256): string
    {
        $root = realpath(config('polis.content').'/documents');
        $path = $root === false ? false : realpath("{$root}/{$language}/{$id}/{$version}.md");
        $source = $path !== false && str_starts_with($path, $root.DIRECTORY_SEPARATOR) && is_file($path)
            ? file_get_contents($path) : false;
        if ($source === false || ! mb_check_encoding($source, 'UTF-8') || ! hash_equals($sha256, hash('sha256', $source))) {
            throw new RuntimeException("Integrità non verificata per {$id} {$version}");
        }

        return $source;
    }
}
