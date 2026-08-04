.PHONY: generate validate preview render clean

generate:
	python scripts/build_course_data.py

validate:
	python scripts/validate.py

preview: generate
	quarto preview

render: generate
	quarto render

clean:
	rm -rf _site .quarto
