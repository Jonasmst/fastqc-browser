import sys
import re


class SampleManager(object):

    def collect_global_summary_stats(self):
        """
        Find the global number of passes, warnings and failures
        """

        # Counters
        num_passes = 0
        num_warnings = 0
        num_failures = 0

        # Loop through all samples
        for sample in self.all_samples:
            num_passes += sample.get_number_of_passes()
            num_warnings += sample.get_number_of_warnings()
            num_failures += sample.get_number_of_failures()

        self.num_passes = num_passes
        self.num_warnings = num_warnings
        self.num_failures = num_failures

    def collect_stats_per_module(self):
        """
        Collects the number of passes, warnings and failures per module
        """

        # Container to store data.
        module_stats = {}  # Format: moduleName: {status: counts}

        # Loop through all samples
        for sample in self.all_samples:
            # Loop through passes
            for read_num, modules in sample.passes.items():
                # Loop through modules
                for module in modules:
                    # Check if it's already in the dict
                    if module not in module_stats.keys():
                        module_stats[module] = {"PASS": 1, "WARN": 0, "FAIL": 0}
                    else:
                        module_stats[module]["PASS"] += 1

            # Loop through warnings
            for read_num, modules in sample.warnings.items():
                # Loop through modules
                for module in modules:
                    # Check if it's already in the dict
                    if module not in module_stats.keys():
                        module_stats[module] = {"PASS": 0, "WARN": 1, "FAIL": 0}
                    else:
                        module_stats[module]["WARN"] += 1

            # Loop through failures
            for read_num, modules in sample.failures.items():
                # Loop through modules
                for module in modules:
                    # Check if it's already in the dict
                    if module not in module_stats.keys():
                        module_stats[module] = {"PASS": 0, "WARN": 0, "FAIL": 1}
                    else:
                        module_stats[module]["FAIL"] += 1

        # Store
        self.module_stats = module_stats

    def get_sample_container_by_status(self, status):
        if status.lower() == "pass":
            return self.passed_samples
        if status.lower() == "warn":
            return self.warned_samples
        if status.lower() == "fail":
            return self.failed_samples

    def set_sample_container_by_status(self, status, container):
        if status.lower() == "pass":
            self.passed_samples = container
        if status.lower() == "warn":
            self.warned_samples = container
        if status.lower() == "fail":
            self.failed_samples = container

    def get_samples_by_module_and_status(self, module_query, status_query):

        container = {}  # Format: sample_name: [read_number, read_number]

        # Loop through all samples
        for sample in self.all_samples:
            # Get status collection
            for read_num, sample_modules in sample.get_collection_by_status(status_query).items():
                if module_query in sample_modules:
                    # Add this sample to the container dict
                    if sample.name not in container.keys():
                        container[sample.name] = [read_num]
                    else:
                        # Check if this read number is in the dict
                        if read_num not in container[sample.name]:
                            container[sample.name].append(read_num)

        # Store in object or return? Or both?
        self.set_sample_container_by_status(status_query, container)
        return container

    def get_html_report_by_name_and_read(self, name, read_num):
        """
        Returns path to the HTML report for a given samplename and read file number.
        """
        # Find sample
        for sample in self.all_samples:
            if sample.name == name:
                return sample.html_reports[read_num]

    def print_samples_by_module_and_status(self, module_query, status_query):
        samples_result = self.get_samples_by_module_and_status(module_query, status_query)

        if len(samples_result) == 0:
            print "No samples with status '%s' in module '%s'" % (status_query, module_query)
            return

        # Print
        print "{0:30}{1:30}{2:10}{3:8}".format("SAMPLE NAME", "MODULE NAME", "STATUS", "FASTQ(s)")

        for name in sorted(samples_result.keys(), key=lambda s: [int(t) if t.isdigit() else t.lower() for t in re.split('(\d+)', s)]):
            read_nums = samples_result[name]
            fastqs_string = " ".join([str(rn) for rn in read_nums])
            print "{0:30}{1:30}{2:10}{3:8}".format(name, module_query, status_query.center(6), fastqs_string.center(8))

    def print_global_summary(self):
        """
        Print global summary (number of passes, warnings and failures)
        """
        num_p = int(self.num_passes)
        num_w = int(self.num_warnings)
        num_f = int(self.num_failures)

        self.print_header(" GLOBAL STATS ", 75, "=")
        print "{0:20}{1:20}{2:20}".format("PASS".center(20), "WARN".center(20), "FAIL".center(20))
        total = float(num_p + num_w + num_f)
        # Percentages
        pct_p = (num_p / total) * 100
        pct_w = (num_w / total) * 100
        pct_f = (num_f / total) * 100

        pct_p_str = "%.2f" % pct_p
        pct_w_str = "%.2f" % pct_w
        pct_f_str = "%.2f" % pct_f

        passes = str(num_p) + " (" + pct_p_str + "%)"
        warns = str(num_w) + " (" + pct_w_str + "%)"
        fails = str(num_f) + " (" + pct_f_str + "%)"

        print "{0:20}{1:20}{2:20}".format(passes.center(20), warns.center(20), fails.center(20))

    def print_module_stats(self):
        """
        Print stats per module
        """

        self.print_header(" MODULE STATS ", 75, "=")
        print '{0:{width}{base}} %5s\t%5s\t%5s'.format("MODULE", base="s", width=30) % ("PASS", "WARN", "FAIL")

        for module in sorted(self.module_stats.keys()):
            stats = self.module_stats[module]
            passes = stats["PASS"]
            warnings = stats["WARN"]
            failures = stats["FAIL"]
            print '{0:{width}{base}} %5d\t%5d\t%5d'.format(module, base="s", width=30) % (passes, warnings, failures)
        print ""

    def get_sample_by_name(self, name):
        """
        Get sample by name
        """
        for sample in self.all_samples:
            if sample.name.lower() == name.lower():
                return sample

    def print_modules_orderby_status(self, status_query):
        """
        Prints a list of modules ordered by the number of failures.
        :param status_query: Status as string: PASS | WARN | FAIL
        """

        self.print_header(" MODULES ", 75, "=")

        print '{0:{width}{base}} %5s\t%5s\t%5s'.format("MODULE", base="s", width=30) % ("PASS", "WARN", "FAIL")

        container = {}  # Format: module_name: failed_counts

        # Loop modules and extract number of failures
        for module, status in self.module_stats.items():
            if module not in container.keys():
                container[module] = status[status_query]
            else:
                print "Warning: print_modules_orderby_status(); dict already contains module"

        # Print list of modules ordered by failures
        for module, fails in sorted(container.items(), key=lambda x: x[1], reverse=True):
            passes = self.module_stats[module]["PASS"]
            warns = self.module_stats[module]["WARN"]
            fails = self.module_stats[module]["FAIL"]

            print '{0:{width}{base}} %5d\t%5d\t%5d'.format(module, base="s", width=30) % (passes, warns, fails)

    def print_samples_orderby_status(self, status_query):
        """
        Prints a list of sample names ordered by a given status
        :param status_query: Status as string: PASS | WARN | FAIL
        """
        print "====================================================="
        print "====================== SAMPLES ======================"
        print "====================================================="
        print '{0:{width}{base}} %5s\t%5s\t%5s'.format("SAMPLE", base="s", width=30) % ("PASS", "WARN", "FAIL")

        container = {}  # Format: sample_name: number_of_failures/passes/warnings

        # Loop samples
        for sample in self.all_samples:
            if sample.name not in container.keys():
                container[sample.name] = sample.get_status_count(status_query)
            else:
                print "Warning: print_samples_orderby_status(); dict already contains sample name"

        # Print ordered list
        for name, fails in sorted(container.items(), key=lambda x: x[1], reverse=True):
            sample = self.get_sample_by_name(name)
            passes = sample.get_number_of_passes()
            warns = sample.get_number_of_warnings()
            fails = sample.get_number_of_failures()
            print '{0:{width}{base}} %5d\t%5d\t%5d'.format(name, base="s", width=30) % (passes, warns, fails)

    def print_sample_details(self, sample_name):
        """
        Prints details about a sample, status for each module
        :param sample_name: The name of the sample
        """

        # Header length for this printout
        header_length = 90

        # Get sample object
        sample = self.get_sample_by_name(sample_name)

        # Print header
        self.print_header(" SAMPLE DETAILS ", header_length, "=")

        # Print overview
        print '{0:30}{1:15s}{2:15s}{3:15s}'.format("SAMPLE NAME", "PASS".center(15), "WARN".center(15), "FAIL".center(15))
        num_p = sample.get_number_of_passes()
        num_w = sample.get_number_of_warnings()
        num_f = sample.get_number_of_failures()
        total = float(num_p + num_w + num_f)
        pct_p = (num_p / total) * 100
        pct_w = (num_w / total) * 100
        pct_f = (num_f / total) * 100
        pct_p_str = "%.2f" % pct_p
        pct_w_str = "%.2f" % pct_w
        pct_f_str = "%.2f" % pct_f
        passes = str(num_p) + " (" + pct_p_str + "%)"
        warns = str(num_w) + " (" + pct_w_str + "%)"
        fails = str(num_f) + " (" + pct_f_str + "%)"
        # Print
        print '{0:30}{1:15s}{2:15s}{3:15s}'.format(sample_name, passes.center(15), warns.center(15), fails.center(15))

        # Get FASTQC data from sample
        for fastqc_number, fastqc_data in sample.fastqc_data.items():

            # Print fastqc data
            print ""
            self.print_header(" FASTQC DATA - FASTQ #" + str(fastqc_number), header_length, "=", False)

            # Print legend
            print "{0:40}{1:50}".format("INFO", "VALUE")

            # Print every entry
            for info_name, value in fastqc_data.items():
                print "{0:40}{1:50}".format(info_name, value)

        # Print modules
        print ""
        self.print_header(" MODULES ", header_length, "=", False)

        num_fastqs = len(sample.html_reports.keys())

        temp_module = "{0:50}".format("NAME")
        temp_fastqs = "".join('{:10}'.format("FASTQ #" + str(s+1)) for s in range(0, num_fastqs))
        print temp_module + temp_fastqs

        # Loop modules
        for module, fastqinfo in sample.modules.items():

            # Create string
            row_module = '{0:50}'.format(module)

            # Create status string
            status_str = "".join(s.center(10) for s in fastqinfo.values())

            print row_module + status_str

    def print_sample_details_by_readnumber(self, sample_name, read_number):
        """
        Same as print_sample_details(), but only for one specific read number
        """

        # Length for headers in this printout
        header_length = 95

        # Get sample object
        sample = self.get_sample_by_name(sample_name)

        # Print header
        self.print_header(" SINGLE-FASTQ SAMPLE DETAIL ", header_length, "=")

        # Loop modules for this read file
        statuses = []
        for module, moduleinfo in sample.modules.items():
            # Get only status for this read number
            module_status = moduleinfo[read_number]
            statuses.append(module_status)

        num_p = statuses.count("PASS")
        num_w = statuses.count("WARN")
        num_f = statuses.count("FAIL")
        total = float(num_p + num_w + num_f)
        pct_p = (num_p / total) * 100
        pct_w = (num_w / total) * 100
        pct_f = (num_f / total) * 100
        pct_p_str = "%.2f" % pct_p
        pct_w_str = "%.2f" % pct_w
        pct_f_str = "%.2f" % pct_f
        passes = str(num_p) + " (" + pct_p_str + "%)"
        warns = str(num_w) + " (" + pct_w_str + "%)"
        fails = str(num_f) + " (" + pct_f_str + "%)"

        # Print
        print '{0:30}{1:15s}{2:15s}{3:15s}{4:15s}'.format("NAME", "FASTQ #", "PASS".center(15), "WARN".center(15), "FAIL".center(15))
        print '{0:30}{1:15s}{2:15s}{3:15s}{4:15s}'.format(sample_name, str(read_number).center(5), passes.center(15), warns.center(15), fails.center(15))

        # Print separator and header
        print ""
        self.print_header(" FASTQC DATA ", header_length, "=", False)

        # Print legend
        print "{0:40}{1:50}".format("INFO", "VALUE")

        # Get FASTQC data from sample
        for fastq_number, fastqc_data in sample.fastqc_data.items():
            # Only print data for this read
            if fastq_number == read_number:
                # Print every entry
                for info_name, value in fastqc_data.items():
                    print "{0:40}{1:50}".format(info_name, value)

        # Print separator and header
        print ""
        self.print_header(" MODULES ", header_length, "=", False)

        # Print legend
        leg_module = "{0:50}".format("NAME")
        leg_status = "".join('{:10}'.format("STATUS"))
        print leg_module + leg_status

        # Loop modules again and print info for each module
        for module, moduleinfo in sample.modules.items():
            # Get only status for this read number
            module_status = moduleinfo[read_number]

            # Create string
            row_module = '{0:50}'.format(module)

            # Create status string
            status_str = "".join('{:10}'.format(module_status))

            # Print
            print row_module + status_str

    def print_header(self, header, size, fillchar, padding=True):
        if padding:
            print "".center(size, fillchar)

        print header.center(size, fillchar)

        if padding:
            print "".center(size, fillchar)

    def __init__(self, sample_list):
        self.all_samples = sample_list
        self.num_passes = 0
        self.num_warnings = 0
        self.num_failures = 0
        self.module_stats = {}
        self.failed_samples = {}
        self.warned_samples = {}
        self.passed_samples = {}

        # Do stuff
        self.collect_global_summary_stats()
        self.collect_stats_per_module()
