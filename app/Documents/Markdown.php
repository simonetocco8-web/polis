<?php

namespace App\Documents;

use League\CommonMark\Environment\Environment;
use League\CommonMark\Extension\CommonMark\CommonMarkCoreExtension;
use League\CommonMark\Extension\CommonMark\Node\Block\Heading;
use League\CommonMark\Extension\CommonMark\Node\Inline\Link;
use League\CommonMark\Node\Block\Document;
use League\CommonMark\Node\StringContainerInterface;
use League\CommonMark\Parser\MarkdownParser;
use League\CommonMark\Renderer\HtmlRenderer;
use RuntimeException;

final class Markdown
{
    private Environment $environment;

    public function __construct()
    {
        $this->environment = new Environment([
            'html_input' => 'strip',
            'allow_unsafe_links' => false,
            'max_nesting_level' => 20,
        ]);
        $this->environment->addExtension(new CommonMarkCoreExtension);
    }

    /** @param array{articles: int, titles: int}|null $structure */
    public function render(string $source, ?array $structure = null, string $articleLinkBase = ''): array
    {
        $document = (new MarkdownParser($this->environment))->parse($source);
        $renderer = new HtmlRenderer($this->environment);
        $outline = [];
        $articles = [];
        $articleBlocks = [];
        $titleIdentifiers = [];
        $targets = [];
        $titleCount = 0;
        $number = null;
        $activeTitle = null;

        foreach ($document->children() as $block) {
            if ($block instanceof Heading) {
                $block->setLevel(max(2, $block->getLevel()));
                $label = $this->headingText($block);
                $id = 'sezione-'.(count($outline) + 1);
                if ($structure !== null) {
                    if (preg_match('/^Articolo\s+(\d+)\b/iu', $label, $match)) {
                        $number = (int) $match[1];
                        if ($number !== count($articles) + 1 || $activeTitle === null || isset($targets['dichiarazione-conclusiva'])) {
                            throw new RuntimeException("Articolo fuori sequenza o senza titolo: {$label}");
                        }
                        $id = 'articolo-'.$number;
                        $articles[$number] = ['label' => $label, 'title' => $activeTitle, 'html' => '', 'text' => ''];
                    } elseif (preg_match('/^Titolo\s+([IVXLCDM]+|\d+)\b/iu', $label, $match)) {
                        $titleIdentifier = strtoupper($match[1]);
                        if (! isset($targets['preambolo']) || isset($targets['dichiarazione-conclusiva']) || isset($titleIdentifiers[$titleIdentifier])) {
                            throw new RuntimeException("Titolo fuori sequenza: {$label}");
                        }
                        $number = null;
                        $activeTitle = $label;
                        $titleIdentifiers[$titleIdentifier] = true;
                        $titleCount++;
                    } elseif (preg_match('/^Preambolo\b/iu', $label)) {
                        if (isset($targets['preambolo']) || $titleCount > 0) {
                            throw new RuntimeException('Preambolo duplicato o fuori sequenza');
                        }
                        $id = 'preambolo';
                    } elseif (preg_match('/^Dichiarazione conclusiva\b/iu', $label)) {
                        if (isset($targets['dichiarazione-conclusiva']) || $articles === []) {
                            throw new RuntimeException('Dichiarazione conclusiva duplicata o fuori sequenza');
                        }
                        $number = null;
                        $id = 'dichiarazione-conclusiva';
                    }
                }
                $block->data->set('attributes/id', $id);
                $outline[] = ['id' => $id, 'label' => $label, 'article' => $id === 'articolo-'.$number ? $number : null];
                $targets[$id] = true;
                if (isset($articles[$number]) && $id === 'articolo-'.$number) {
                    continue;
                }
            }
            if ($number !== null) {
                $articleBlocks[$number][] = $block;
            }
        }

        if ($structure !== null) {
            if (! isset($targets['preambolo']) || ! isset($targets['dichiarazione-conclusiva']) || $titleCount !== $structure['titles'] || count($articles) !== $structure['articles']) {
                throw new RuntimeException('La struttura costituzionale non corrisponde al manifest');
            }
            $this->validateInternalLinks($document, $targets);
        }

        $fullHtml = (string) $renderer->renderDocument($document);
        foreach ($articles as $index => &$article) {
            $blocks = $articleBlocks[$index] ?? [];
            foreach ($blocks as $block) {
                $walker = $block->walker();
                while ($event = $walker->next()) {
                    $node = $event->getNode();
                    if ($event->isEntering() && $node instanceof Link && str_starts_with($node->getUrl(), '#')) {
                        $node->setUrl($articleLinkBase.$node->getUrl());
                    }
                }
            }
            $article['html'] = $renderer->renderNodes($blocks);
            $article['text'] = html_entity_decode(strip_tags($article['html']), ENT_QUOTES | ENT_HTML5, 'UTF-8');
        }

        return ['html' => $fullHtml, 'outline' => $outline, 'articles' => $articles];
    }

    private function headingText(Heading $heading): string
    {
        $label = '';
        $walker = $heading->walker();
        while ($event = $walker->next()) {
            $node = $event->getNode();
            if ($event->isEntering() && $node instanceof StringContainerInterface) {
                $label .= $node->getLiteral();
            }
        }

        return trim($label);
    }

    /** @param array<string, bool> $targets */
    private function validateInternalLinks(Document $document, array $targets): void
    {
        $walker = $document->walker();
        while ($event = $walker->next()) {
            $node = $event->getNode();
            if ($event->isEntering() && $node instanceof Link && str_starts_with($node->getUrl(), '#')) {
                $target = rawurldecode(substr($node->getUrl(), 1));
                if (! isset($targets[$target])) {
                    throw new RuntimeException("Riferimento costituzionale mancante: {$target}");
                }
            }
        }
    }
}
