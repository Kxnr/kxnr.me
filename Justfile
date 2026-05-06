build:
    mkdir -p docs/css
    metalabel build src docs --pre-build pre-build.scm
    npx tailwindcss -i ./css/source.css -o ./docs/css/output.css --minify

serve:
    python3 -m http.server 8000 --directory docs
