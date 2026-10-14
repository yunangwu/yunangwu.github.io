# Regenerate _publications/ from _bibliography/publications.bib before every build
# (including rebuilds triggered by `jekyll serve` when the .bib file changes).
Jekyll::Hooks.register :site, :after_reset do |site|
  script = File.join(site.source, "scripts", "bib2pubs.py")
  system("python3", script) or raise "bib2pubs.py failed"
end
