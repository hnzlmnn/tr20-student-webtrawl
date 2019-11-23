find webtrawl -iname "*.pyc" | xargs rm -f
python -m py_compile server.py
python -m compileall webtrawl
mkdir -p dist/
rm -rf dist/*
find webtrawl __pycache__ -iname "*.pyc" | while read file; do
	target=$(echo "dist/$file" | sed 's|/__pycache__||g' | sed 's/.cpython-37//g')
	mkdir -p "$(dirname "$target")"
	cp "$file" "$target"
done
