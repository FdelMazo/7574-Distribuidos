KAGGLE_DATASET = pavellexyr/the-reddit-irl-dataset

get-data:
	test -n "$(KAGGLE_USERNAME)"  # Don't forget to set up KAGGLE_USERNAME
	test -n "$(KAGGLE_KEY)"  # Don't forget to set up KAGGLE_KEY
	test -n "$(shell which kaggle)"  # Don't forget to pip install kaggle
	kaggle datasets download $(KAGGLE_DATASET) -f dataset.zip
	unzip dataset.zip -d data
	rm dataset.zip
.PHONY: get-data
