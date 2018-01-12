import sys
from cate.util.cli import run_main, SubCommandCommand

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

#: Name of command line executable
CLI_NAME = 'multiply2'
CLI_DESCRIPTION = 'The MULTIPLY Command Line Interface'

__version__ = '0.1'

HELP_TEXT = 'Performs Pre-Processing on S1A L1C Data. This step is a prerequisite for using the data in the' \
            'inference engine.'
CONFIG_HELP_TEXT = 'A config file in YAML format. This file holds information on the other parameters.'
ROI_HELP_TEXT = 'The spatial extent of the region of interest, given as wkt string. EO products that intersect this ' \
                'zone will be included. If not given, it is assumed that the whole globe is the region of interest.'
YEAR_HELP_TEXT = '?'
GPT_DIRECTORY_HELP_TEXT = 'The path to the GPT executable of the SNAP installation that shall be used for pre ' \
                          'processing. Mandatory.'
INPUT_DIRECTORY_HELP_TEXT = 'The path to the directory containing all the S1A L1C files that shall be pre-processed. ' \
                            'Mandatory.'
OUTPUT_DIRECTORY_HELP_TEXT = 'The path to the folder to which the output shall be written. If no such path is ' \
                             'provided, a sub-directory will be created in the input directory. Optional.'


class DoSarPreProcessingCommand(SubCommandCommand):

    @classmethod
    def name(cls):
        return 'do_sar_pre_processing'

    @classmethod
    def parser_kwargs(cls):

        return dict(help=HELP_TEXT,
                    description=HELP_TEXT)

    @classmethod
    def configure_parser_and_subparsers(cls, parser, subparsers):
        parser.add_argument('--config', '-c', help=CONFIG_HELP_TEXT)
        parser.add_argument('--roi', '-r', help=ROI_HELP_TEXT)
        parser.add_argument('--year', '-y', help=YEAR_HELP_TEXT)
        parser.add_argument('--gpt', '-g', help=GPT_DIRECTORY_HELP_TEXT)
        parser.add_argument('--inputdir', '-i', help=INPUT_DIRECTORY_HELP_TEXT)
        parser.add_argument('--outputdir', '-o', help=OUTPUT_DIRECTORY_HELP_TEXT)
        # parser.set_defaults(sub_command_function=cls._execute_list)


# list of commands supported by the CLI. Entries are classes derived from :py:class:'Command' class-
COMMAND_REGISTRY = [DoSarPreProcessingCommand]


def main(args=None) -> int:
    # noinspection PyTypeChecker
    return run_main(CLI_NAME,
                    CLI_DESCRIPTION,
                    __version__,
                    COMMAND_REGISTRY,
                    license_text='license text',
                    docs_url='url to docs',
                    error_message_trimmer=None,
                    args=args)

if __name__ == '__main__':
    sys.exit(main())
