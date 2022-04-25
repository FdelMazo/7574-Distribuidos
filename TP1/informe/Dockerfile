FROM dalibo/pandocker:latest
COPY informe /
COPY README.md /
ENTRYPOINT ["pandoc", "/header.yaml", "/README.md", "--output", "/informe.pdf"]
