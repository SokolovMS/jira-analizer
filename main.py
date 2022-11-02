import logging

import config
import scripts.analyze as analyze
import scripts.parser as parser
from scripts import download, files

logging.root.setLevel(logging.NOTSET)


def re_fetch(clear=False):
	if clear:
		files.clear_dir(config.issues_rest)
	download.fetch_issues()


def re_parse(clear=False):
	if clear:
		files.clear_dir(config.issues_dir)
	parser.parse_everything()


def main():
	re_fetch(clear=True)
	re_parse(clear=True)

	analyze.gather_stats(days_back=10000)


if __name__ == '__main__':
	main()
	logging.info("Done")
