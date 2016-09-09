import argparse
import os
import sys
from Sample import Sample
from SampleManager import SampleManager
from AutoCompleter import MyCompleter
import webbrowser
import readline


def handle_arguments():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-i", "--input-directory", help="Path to parent directory containing all sample directories. Provide absolute paths", required=False)
    parser.add_argument("-h", "--help", help="Print help text", action="store_true", required=False)
    args = parser.parse_args()

    if args.help:
        print_help()
        sys.exit()

    if not args.input_directory:
        print_help()
        sys.exit()

    # Get path from args
    parent_dir = args.input_directory

    return parent_dir


def setup_samples(parent_dir):

    print "Reading directory %s ..." % parent_dir

    # Container to keep sample objects
    samples = []

    # Get subdirectories in parent dir
    subdirs = [os.path.join(parent_dir, s) for s in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, s))]
    for sd in subdirs:
        # Loop files in sample directory
        abs_sample_path = os.path.abspath(os.path.join(parent_dir, sd))

        # Create sample object
        sample = Sample(abs_sample_path, os.path.abspath(parent_dir))

        # Add to samples collection
        samples.append(sample)

    # Return all samples
    return samples


def open_html_report(path, sample_manager, sample_name, read_number):
    """
    Opens a given html file in a webbrowser. If there is no webbrowser available,
    a textual representation of the report (i.e. without figures) are fetched and displayed.
    """
    try:
        webbrowser.get()
        webbrowser.open("file://" + os.path.realpath(path))
    except webbrowser.Error as e:
        print "Something went wrong when opening webbrowser (Error: %s). Fall back to textual representation:" % e
        sample_manager.print_sample_details_by_readnumber(sample_name, read_number)


def print_query_help():
    print "=============== SUPPORTED COMMANDS ==============="
    print "help                               - prints this message"
    print "exit                               - quit"
    print "open_sample_html_report            - open HTML report in browser (if available)"
    print "print_global_stats                 - prints total number of PASS/WARN/FAILs"
    print "print_module_stats                 - prints stats (PASS/WARN/FAIL) per module"
    print "print_sample_details               - prints stats for a given sample"
    print "print_samples_by_status_in_module  - prints the samples that PASS/WARN/FAIL a given module"
    print "print_all_samples_orderby_status   - prints all samples ordered by PASS/WARN/FAILs"
    print "print_all_modules_orderby_status   - prints all modules ordered by PASS/WARN/FAILs"


def print_help():
    print "================================================"
    print "============== FASTQC BROWSER =================="
    print "================================================"
    print "The FastQC browser expects a single argument:"
    print "-i / --input-directory DIRECTORY"
    print "where DIRECTORY is the path to a directory containing"
    print "one folder for each sample, e.g.:"
    print ""
    print "-fastqc_output/"
    print "  |-- sample1/"
    print "      |-- sample1_1.zip"
    print "      |-- sample1_2.zip"
    print "      |-- report.html"
    print "  |-- sample2/"
    print "      |-- sample2_1.zip"
    print "      |-- sample2_2.zip"
    print "      |-- report.html"
    print "  |-- sample3/"
    print "      |-- sample3_1.zip"
    print "      |-- sample3_2.zip"
    print "      |-- report.html"
    print ""
    print "Example:"
    print ""
    print "python fastqc_browser.py --input-directory fastqc_output"
    print ""
    print "After everything is loaded, you'll be prompted for keyboard input."
    print "Type 'help' to see all available commands, or press the <TAB> "
    print "key (sometimes twice) for suggestions and auto-completion."
    print "Please provide only a single supported command, then press <ENTER>,"
    print "then press <TAB> again to see supported commands for the new level. E.g.:"
    print ""
    print "> open_sample_report <ENTER>"
    print ">> sample1 <ENTER>"
    print ">>> 1 <ENTER>"
    print "================================================"


def read_input(sample_manager):
    """
    Continuous loop that reads keyboard input and interprets queries
    """

    supported_start_commands = [
        "help",
        "exit",
        "open_sample_html_report",
        "print_global_stats",
        "print_module_stats",
        "print_sample_details",
        "print_samples_by_status_in_module",
        "print_all_samples_orderby_status",
        "print_all_modules_orderby_status"
    ]

    supported_module_names = [
        "per_tile_sequence_quality",
        "per_base_sequence_quality",
        "sequence_duplication_levels",
        "per_base_sequence_content",
        "per_sequence_gc_content",
        "sequence_length_distribution",
        "kmer_content",
        "basic_statistics",
        "adapter_content",
        "overrepresented_sequences",
        "per_base_n_content",
        "per_sequence_quality_scores"
    ]

    supported_statuses = ["PASS", "WARN", "FAIL"]

    modules = {
        "pertilesequencequality": "Per tile sequence quality",
        "perbasesequencequality": "Per base sequence quality",
        "sequenceduplicationlevels": "Sequence Duplication Levels",
        "perbasesequencecontent": "Per base sequence content",
        "persequencegccontent": "Per sequence GC content",
        "sequencelengthdistribution": "Sequence Length Distribution",
        "kmercontent": "Kmer Content",
        "basicstatistics": "Basic Statistics",
        "adaptercontent": "Adapter Content",
        "overrepresentedsequences": "Overrepresented sequences",
        "perbasencontent": "Per base N content",
        "persequencequalityscores": "Per sequence quality scores"
    }

    all_sample_names = [s.name for s in sample_manager.all_samples]

    print "===== SUBMIT QUERY ====="
    print "(type 'help' for help)"
    print "(press <TAB> for auto-completion)"

    while True:
        # Setup auto-completer
        completer = MyCompleter(supported_start_commands)
        readline.set_completer(completer.complete)
        readline.parse_and_bind('tab: complete')

        # Read input from keyboard
        choice = raw_input("> ").lower()

        # Quit
        if choice.startswith("exit"):
            print "Exiting.."
            break

        # Help
        if choice.startswith("help"):
            print_query_help()
            continue

        # Read HTML report
        if choice.startswith("open_sample_html_report"):

            # Set auto-completer for sample names
            completer = MyCompleter(all_sample_names)
            readline.set_completer(completer.complete)
            readline.parse_and_bind('tab: complete')

            # Read sample name from keyboard
            sample_name = raw_input(">> Sample name: ")

            # Check if sample name is valid
            if sample_name not in all_sample_names:
                print "DOES NOT COMPUTE; INVALID SAMPLE NAME"
                continue

            # Setup auto-completer for read number
            sample = sample_manager.get_sample_by_name(sample_name)
            read_num_options = [str(k) for k in sample.read_dirs.keys()]
            completer = MyCompleter(read_num_options)
            readline.set_completer(completer.complete)
            readline.parse_and_bind('tab: complete')

            # Read read number from input
            read_number = int(raw_input(">>> Read file number: "))

            report = sample_manager.get_html_report_by_name_and_read(sample_name, read_number)
            open_html_report(report, sample_manager, sample_name, read_number)

            continue

        # Print sample details
        if choice.lower().startswith("print_sample_details"):
            # Setup auto-completer for sample names
            completer = MyCompleter(all_sample_names)
            readline.set_completer(completer.complete)
            readline.parse_and_bind('tab: complete')

            # Read sample name from keyboard
            sample_name = raw_input(">> Sample name: ")

            # Check if sample name is valid
            if sample_name not in all_sample_names:
                print "BLEEP BLOP, DOES NOT COMPUTE! INVALID SAMPLE NAME: %s" % sample_name
                continue

            # Print sample details
            sample_manager.print_sample_details(sample_name)
            continue

        # Print samples by module and status
        if choice.lower().startswith("print_samples_by_status_in_module"):
            # Setup auto-completer for module names
            completer = MyCompleter(supported_module_names)
            readline.set_completer(completer.complete)
            readline.parse_and_bind('tab: complete')

            # Read module name
            module_name = raw_input(">> Module name: ")

            # Check if module name is valid
            if module_name not in supported_module_names:
                print "BLEEP BLOP, DOES NOT COMPUTE! INVALID MODULE NAME"
                continue

            # Get module
            lookup = module_name.replace(" ", "").replace("_", "")
            module_query = modules[lookup]

            # Setup auto-completer for status
            completer = MyCompleter(supported_statuses)
            readline.set_completer(completer.complete)
            readline.parse_and_bind('tab: complete')

            # Read status
            status_name = raw_input(">>> Status: ")

            # Check if status name is valid
            if status_name not in supported_statuses:
                print "BLEEP BLOP, DOES NOT COMPUTE! INVALID STATUS"
                continue

            # Print samples by module and status
            sample_manager.print_samples_by_module_and_status(module_query=module_query, status_query=status_name)
            continue

        # Print global stats
        if choice.startswith("print_global_stats"):
            sample_manager.print_global_summary()
            continue

        # Print module stats
        if choice.startswith("print_module_stats"):
            sample_manager.print_module_stats()
            continue

        # Print modules, order by PASS, FAIL or WARN
        if choice.startswith("print_all_modules_orderby_status"):

            # Setup auto-completer for statuses
            completer = MyCompleter(supported_statuses)
            readline.set_completer(completer.complete)
            readline.parse_and_bind('tab: complete')

            # Read status
            status_name = raw_input("> Status: ")

            # Validate
            if status_name not in supported_statuses:
                print "BLEED BLOP, DOES NOT COMPUTE! INVALID STATUS NAME: " % status_name
                continue

            # Print sorted modules
            sample_manager.print_modules_orderby_status(status_name)
            continue

        # Print samples, order by PASS, FAIL or WARN
        if choice.startswith("print_all_samples_orderby_status"):

            # Setup auto-completer for status
            completer = MyCompleter(supported_statuses)
            readline.set_completer(completer.complete)
            readline.parse_and_bind('tab: complete')

            # Read status
            status_name = raw_input("> Order samples by status: ")

            # Validate
            if status_name not in supported_statuses:
                print "BLEEP BLOP, DOES NOT COMPUTE! INVALID STATUS  NAME: %s" % status_name
                continue

            # Print samples ordered by status
            sample_manager.print_samples_orderby_status(status_name)
            continue


def main():
    parent_dir = handle_arguments()

    # Parse parent dir
    samples = setup_samples(parent_dir)

    # Create sample manager
    sample_manager = SampleManager(samples)

    # Print global stats
    #sample_manager.print_global_summary()
    #sample_manager.print_module_stats()

    # Wait for input
    read_input(sample_manager)

if __name__ == "__main__":
    main()
