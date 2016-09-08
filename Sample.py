import os
import zipfile
import shutil
import sys

class Sample(object):

    def handle_read_libraries(self):
        # TODO: Add to documentation that these zip-files are expected (required)
        # Find zipped files
        zipped_files = [f for f in os.listdir(self.main_directory) if f.endswith(".zip")]

        # If no zip-files are found, exit
        if len(zipped_files) == 0:
            print "ERROR: No zip-files containing FastQC info found in %s. Exiting" % self.main_directory
            sys.exit()

        # If there's more than 2 zip-files, I don't know what to do with them
        if len(zipped_files) > 2:
            print "ERROR: More than two (%d) zip-files found in %s. I don't know how to handle more than 2. Exiting." % (len(zipped_files), self.main_directory)
            sys.exit()

        # Handle zip files
        for f in sorted(zipped_files):
            # Get sample dir path
            sample_path = os.path.join(self.parent_dir, self.main_directory)

            # Get absolute path
            abs_path = os.path.abspath(os.path.join(sample_path, f))

            # Unzip file
            zip_ref = zipfile.ZipFile(abs_path, "r")

            # Get unzipped dirname
            unzipped_dirname = abs_path.split(".zip")[0]

            # Delete unzipped dir if already exists
            if os.path.exists(unzipped_dirname) and os.path.isdir(unzipped_dirname):
                shutil.rmtree(unzipped_dirname)

            # Extract content
            zip_ref.extractall(sample_path)

            # Assign read-number according to position in list of zip-files
            pos = sorted(zipped_files).index(f) + 1
            self.read_dirs[pos] = unzipped_dirname

    def locate_summary_files(self):
        # Traverse read directories and find summary files
        for read_number, read_dir in self.read_dirs.items():

            # Get sample path
            sample_path = os.path.join(self.parent_dir, self.main_directory)

            # Get absolute path
            abs_read_dir = os.path.join(sample_path, read_dir)

            # Expected path
            summary_path = os.path.join(abs_read_dir, "summary.txt")
            if not os.path.exists(summary_path):
                print "No summary file found in %s in sample %s" % (read_dir, self.name)
                continue
            else:
                # Store reference to summary file
                if read_number not in self.summary_files.keys():
                    self.summary_files[read_number] = summary_path
                else:
                    print "Summary file for read %d already present in sample %s" % (read_number, self.name)

    def locate_html_reports(self):
        # Traverse read directories and find report files
        for read_number, read_dir in self.read_dirs.items():

            # Get sample path
            sample_path = os.path.join(self.parent_dir, self.main_directory)

            # Get absolute path
            abs_read_dir = os.path.join(sample_path, read_dir)

            # Expected path
            html_path = os.path.join(abs_read_dir, "fastqc_report.html")
            if not os.path.exists(html_path):
                print "No HTML report file found for read file %d in sample %s" % (read_number, self.name)
            else:
                # Store reference to report file
                if read_number not in self.html_reports.keys():
                    self.html_reports[read_number] = html_path
                else:
                    print "Report file already present for read %d in sample %s" % (read_number, self.name)

    def parse_summaries(self):

        # Loop summary files
        for read_num, sum_file in self.summary_files.items():
            # Read summary file
            with open(sum_file) as sf:
                # Read each line
                for line in sf.readlines():
                    # Split by tabs to get: PASS/WARN/FAIL MODULE FASTQ-file
                    stats = line.split("\t")
                    status = stats[0]
                    module = stats[1]

                    # Update module information
                    if module not in self.modules.keys():
                        self.modules[module] = {read_num: status}
                    else:
                        # Check if read_num is not already in there
                        if read_num not in self.modules[module].keys():
                            self.modules[module][read_num] = status

                    # Update status
                    if status == "WARN":
                        if read_num not in self.warnings.keys():
                            self.warnings[read_num] = [module]
                        else:
                            self.warnings[read_num].append(module)
                    elif status == "PASS":
                        if read_num not in self.passes.keys():
                            self.passes[read_num] = [module]
                        else:
                            self.passes[read_num].append(module)
                    elif status == "FAIL":
                        if read_num not in self.failures:
                            self.failures[read_num] = [module]
                        else:
                            self.failures[read_num].append(module)

    def get_html_report(self, read_number):
        # TODO: Sanity check
        return self.html_reports[read_number]

    def get_number_of_passes(self):
        # Add together number of passes for both read files
        total = 0
        for read_num, modules in self.passes.items():
            total += len(modules)
        return total

    def get_number_of_warnings(self):
        # Add together number of passes for both read files
        total = 0
        for read_num, modules in self.warnings.items():
            total += len(modules)
        return total

    def get_number_of_failures(self):
        # Add together number of passes for both read files
        total = 0
        for read_num, modules in self.failures.items():
            total += len(modules)
        return total

    def get_status_count(self, status_query):
        if status_query.lower() == "pass":
            return self.get_number_of_passes()
        if status_query.lower() == "warn":
            return self.get_number_of_warnings()
        if status_query.lower() == "fail":
            return self.get_number_of_failures()

    def get_collection_by_status(self, status):
        if status.lower() == "pass":
            return self.passes
        if status.lower() == "warn":
            return self.warnings
        if status.lower() == "fail":
            return self.failures

    def __init__(self, sample_dir, parent_dir):
        self.name = os.path.basename(os.path.normpath(sample_dir))
        self.main_directory = sample_dir
        self.parent_dir = parent_dir
        self.read_dirs = {}  # Format: readEndNumber: directoryName, e.g. 2:path_to_fastq2
        self.summary_files = {}
        self.html_reports = {}
        self.warnings = {}  # Format: readNumber: [modules]
        self.passes = {}
        self.failures = {}
        self.modules = {}  # Format: module_name: {read_num: status}

        # Do stuff
        self.handle_read_libraries()
        self.locate_summary_files()
        self.locate_html_reports()
        self.parse_summaries()