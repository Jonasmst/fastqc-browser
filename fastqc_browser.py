import argparse
import os
import sys
from Sample import Sample
from SampleManager import SampleManager
from AutoCompleter import MyCompleter
import webbrowser
import readline

module_descriptions = {
        # Per tile sequence quality
        "per_tile_sequence_quality":
        """
== Per Tile Sequence Quality ==
(Link: http://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/12%20Per%20Tile%20Sequence%20Quality.html)

*Summary*
This graph will only appear in your analysis results if you're using an Illumina library which retains its original sequence identifiers. Encoded in these is the flowcell tile from which each read came. The graph allows you to look at the quality scores from each tile across all of your bases to see if there was a loss in quality associated with only one part of the flowcell. The plot shows the deviation from the average quality for each tile. The colours are on a cold to hot scale, with cold colours being positions where the quality was at or above the average for that base in the run, and hotter colours indicate that a tile had worse qualities than other tiles for that base. In the example below you can see that certain tiles show consistently poor quality. A good plot should be blue all over.

*Kmer profiles*
Reasons for seeing warnings or errors on this plot could be transient problems such as bubbles going through the flowcell, or they could be more permanent problems such as smudges on the flowcell or debris inside the flowcell lane.

*Warning*
This module will issue a warning if any tile shows a mean Phred score more than 2 less than the mean for that base across all tiles.

*Failure*
This module will issue a warning if any tile shows a mean Phred score more than 5 less than the mean for that base across all tiles.

*Common reasons for warnings*
Whilst warnings in this module can be triggered by individual specific events we have also observed that greater variation in the phred scores attributed to tiles can also appear when a flowcell is generally overloaded. In this case events appear all over the flowcell rather than being confined to a specific area or range of cycles. We would generally ignore errors which mildly affected a small number of tiles for only 1 or 2 cycles, but would pursue larger effects which showed high deviation in scores, or which persisted for several cycles.
        """,
        # Per base sequence quality
        "per_base_sequence_quality":
        """
== Per Base Sequence Quality ==
(Link: http://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/2%20Per%20Base%20Sequence%20Quality.html)

*Summary*
This view shows an overview of the range of quality values across all bases at each position in the FastQ file.
For each position a BoxWhisker type plot is drawn. The elements of the plot are as follows:
\t- The central red line is the median value
\t- The yellow box represents the inter-quartile range (25-75%)
\t- The upper and lower whiskers represent the 10% and 90% points
\t- The blue line represents the mean quality
\t- The y-axis on the graph shows the quality scores. The higher the score the better the base call.
\t- The background of the graph divides the y axis into very good quality calls (green), calls of
\t  reasonable quality (orange), and calls of poor quality (red). The quality of calls on most
\t  platforms will degrade as the run progresses, so it is common to see base calls falling
\t  into the orange area towards the end of a read.

It should be mentioned that there are number of different ways to encode a quality score in a FastQ file. FastQC attempts to automatically determine which encoding method was used, but in some very limited datasets it is possible that it will guess this incorrectly (ironically only when your data is universally very good!). The title of the graph will describe the encoding FastQC thinks your file used.
Results from this module will not be displayed if your input is a BAM/SAM file in which quality scores have not been recorded.

*Warning*
A warning will be issued if the lower quartile for any base is less than 10, or if the median for any base is less than 25.

*Failure*
This module will raise a failure if the lower quartile for any base is less than 5 or if the median for any base is less than 20.

*Common reasons for warnings*
The most common reason for warnings and failures in this module is a general degradation of quality over the duration of long runs. In general sequencing chemistry degrades with increasing read length and for long runs you may find that the general quality of the run falls to a level where a warning or error is triggered.
If the quality of the library falls to a low level then the most common remedy is to perform quality trimming where reads are truncated based on their average quality. For most libraries where this type of degradation has occurred you will often be simultaneously running into the issue of adapter read-through so a combined adapter and quality trimming step is often employed.
Another possibility is that a warn / error is triggered because of a short loss of quality earlier in the run, which then recovers to produce later good quality sequence. This can happen if there is a transient problem with the run (bubbles passing through a flowcell for example). You can normally see this type of error by looking at the per-tile quality plot (if available for your platform). In these cases trimming is not advisable as it will remove later good sequence, but you might want to consider masking bases during subsequent mapping or assembly.
If your library has reads of varying length then you can find a warning or error is triggered from this module because of very low coverage for a given base range. Before committing to any action, check how many sequences were responsible for triggering an error by looking at the sequence length distribution module results.
        """,
        # Sequence duplication levels
        "sequence_duplication_levels":
        """
== Duplicate Sequences ==
(Link: http://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/8%20Duplicate%20Sequences.html)

*Summary*
In a diverse library most sequences will occur only once in the final set. A low level of duplication may indicate a very high level of coverage of the target sequence, but a high level of duplication is more likely to indicate some kind of enrichment bias (eg PCR over amplification).
This module counts the degree of duplication for every sequence in a library and creates a plot showing the relative number of sequences with different degrees of duplication.
To cut down on the memory requirements for this module only sequences which first appear in the first 100,000 sequences in each file are analysed, but this should be enough to get a good impression for the duplication levels in the whole file. Each sequence is tracked to the end of the file to give a representative count of the overall duplication level. To cut down on the amount of information in the final plot any sequences with more than 10 duplicates are placed into grouped bins to give a clear impression of the overall duplication level without having to show each individual duplication value.
Because the duplication detection requires an exact sequence match over the whole length of the sequence, any reads over 75bp in length are truncated to 50bp for the purposes of this analysis. Even so, longer reads are more likely to contain sequencing errors which will artificially increase the observed diversity and will tend to underrepresent highly duplicated sequences.
The plot shows the proportion of the library which is made up of sequences in each of the different duplication level bins. There are two lines on the plot. The blue line takes the full sequence set and shows how its duplication levels are distributed. In the red plot the sequences are de-duplicated and the proportions shown are the proportions of the deduplicated set which come from different duplication levels in the original data.
In a properly diverse library most sequences should fall into the far left of the plot in both the red and blue lines. A general level of enrichment, indicating broad oversequencing in the library will tend to flatten the lines, lowering the low end and generally raising other categories. More specific enrichments of subsets, or the presence of low complexity contaminants will tend to produce spikes towards the right of the plot. These high duplication peaks will most often appear in the red trace as they make up a high proportion of the original library, but usually disappear in the blue trace as they make up an insignificant proportion of the deduplicated set. If peaks persist in the blue trace then this suggests that there are a large number of different highly duplicated sequences which might indicate either a contaminant set or a very severe technical duplication.
The module also calculates an expected overall loss of sequence were the library to be deduplicated. This headline figure is shown at the top of the plot and gives a reasonable impression of the potential overall level of loss.

*Warning*
This module will issue a warning if non-unique sequences make up more than 20% of the total.

*Failure*
This module will issue a error if non-unique sequences make up more than 50% of the total.

*Common reasons for warnings*
The underlying assumption of this module is of a diverse unenriched library. Any deviation from this assumption will naturally generate duplicates and can lead to warnings or errors from this module.
In general there are two potential types of duplicate in a library, technical duplicates arising from PCR artefacts, or biological duplicates which are natural collisions where different copies of exactly the same sequence are randomly selected. From a sequence level there is no way to distinguish between these two types and both will be reported as duplicates here.
A warning or error in this module is simply a statement that you have exhausted the diversity in at least part of your library and are re-sequencing the same sequences. In a supposedly diverse library this would suggest that the diversity has been partially or completely exhausted and that you are therefore wasting sequencing capacity. However in some library types you will naturally tend to over-sequence parts of the library and therefore generate duplication and will therefore expect to see warnings or error from this module.
In RNA-Seq libraries sequences from different transcripts will be present at wildly different levels in the starting population. In order to be able to observe lowly expressed transcripts it is therefore common to greatly over-sequence high expressed transcripts, and this will potentially create large set of duplicates. This will result in high overall duplication in this test, and will often produce peaks in the higher duplication bins. This duplication will come from physically connected regions, and an examination of the distribution of duplicates in a specific genomic region will allow the distinction between over-sequencing and general technical duplication, but these distinctions are not possible from raw fastq files. A similar situation can arise in highly enriched ChIP-Seq libraries although the duplication there is less pronounced. Finally, if you have a library where the sequence start points are constrained (a library constructed around restriction sites for example, or an unfragmented small RNA library) then the constrained start sites will generate huge dupliction levels which should not be treated as a problem, nor removed by deduplication. In these types of library you should consider using a system such as random barcoding to allow the distinction of technical and biological duplicates.
        """,
        # Per base sequence content
        "per_base_sequence_content":
        """
== Per Base Sequence Content ==
(Link: http://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/4%20Per%20Base%20Sequence%20Content.html)

*Summary*
Per Base Sequence Content plots out the proportion of each base position in a file for which each of the four normal DNA bases has been called.
In a random library you would expect that there would be little to no difference between the different bases of a sequence run, so the lines in this plot should run parallel with each other. The relative amount of each base should reflect the overall amount of these bases in your genome, but in any case they should not be hugely imbalanced from each other.
It's worth noting that some types of library will always produce biased sequence composition, normally at the start of the read. Libraries produced by priming using random hexamers (including nearly all RNA-Seq libraries) and those which were fragmented using transposases inherit an intrinsic bias in the positions at which reads start. This bias does not concern an absolute sequence, but instead provides enrichement of a number of different K-mers at the 5' end of the reads. Whilst this is a true technical bias, it isn't something which can be corrected by trimming and in most cases doesn't seem to adversely affect the downstream analysis. It will however produce a warning or error in this module.

*Warning*
This module issues a warning if the difference between A and T, or G and C is greater than 10% in any position.

*Failure*
This module will fail if the difference between A and T, or G and C is greater than 20% in any position.

*Common reasons for warnings*
There are a number of common scenarios which would ellicit a warning or error from this module.
\t1. Overrepresented sequences: If there is any evidence of overrepresented sequences such
\t   as adapter dimers or rRNA in a sample then these sequences may bias the overall
\t   composition and their sequence will emerge from this plot.
\t2. Biased fragmentation: Any library which is generated based on the ligation of
\t   random hexamers or through tagmentation should theoretically have good diversity
\t   through the sequence, but experience has shown that these libraries always have
\t   a selection bias in around the first 12bp of each run. This is due to a biased
\t   selection of random primers, but doesn't represent any individually biased sequences.
\t   Nearly all RNA-Seq libraries will fail this module because of this bias, but this is
\t   not a problem which can be fixed by processing, and it doesn't seem to adversely
\t   affect the ablity to measure expression.
\t3. Biased composition libraries: Some libraries are inherently biased in their sequence
\t   composition. The most obvious example would be a library which has been treated with
\t   sodium bisulphite which will then have converted most of the cytosines to thymines,
\t   meaning that the base composition will be almost devoid of cytosines and will thus
\t   trigger an error, despite this being entirely normal for that type of library
\t4. If you are analysing a library which has been aggressivley adapter trimmed then you
\t   will naturally introduce a composition bias at the end of the reads as sequences which
\t   happen to match short stretches of adapter are removed, leaving only sequences which
\t   do not match. Sudden deviations in composition at the end of libraries which have
\t   undergone aggressive trimming are therefore likely to be spurious.
        """,
        # Per sequence GC content
        "per_sequence_gc_content":
        """
== Per Sequence GC Content ==
(Link: http://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/5%20Per%20Sequence%20GC%20Content.html)

*Summary*
This module measures the GC content across the whole length of each sequence in a file and compares it to a modelled normal distribution of GC content.
In a normal random library you would expect to see a roughly normal distribution of GC content where the central peak corresponds to the overall GC content of the underlying genome. Since we don't know the the GC content of the genome the modal GC content is calculated from the observed data and used to build a reference distribution.
An unusually shaped distribution could indicate a contaminated library or some other kinds of biased subset. A normal distribution which is shifted indicates some systematic bias which is independent of base position. If there is a systematic bias which creates a shifted normal distribution then this won't be flagged as an error by the module since it doesn't know what your genome's GC content should be.

*Warning*
A warning is raised if the sum of the deviations from the normal distribution represents more than 15% of the reads.

*Failure*
This module will indicate a failure if the sum of the deviations from the normal distribution represents more than 30% of the reads.

*Common reasons for warnings*
Warnings in this module usually indicate a problem with the library. Sharp peaks on an otherwise smooth distribution are normally the result of a specific contaminant (adapter dimers for example), which may well be picked up by the overrepresented sequences module. Broader peaks may represent contamination with a different species.
        """,
        # Sequence length distribution
        "sequence_length_distribution":
        """
== Sequence Length Distribution ==
(Link: http://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/7%20Sequence%20Length%20Distribution.html)

*Summary*
Some high throughput sequencers generate sequence fragments of uniform length, but others can contain reads of wildly varying lengths. Even within uniform length libraries some pipelines will trim sequences to remove poor quality base calls from the end.
This module generates a graph showing the distribution of fragment sizes in the file which was analysed.
In many cases this will produce a simple graph showing a peak only at one size, but for variable length FastQ files this will show the relative amounts of each different size of sequence fragment.

*Warning*
This module will raise a warning if all sequences are not the same length.

*Failure*
This module will raise an error if any of the sequences have zero length.

*Common reasons for warnings*
For some sequencing platforms it is entirely normal to have different read lengths so warnings here can be ignored.
        """,
        # Kmer content
        "kmer_content":
        """
== Kmer Content ==
(Link: http://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/11%20Kmer%20Content.html)

*Summary*
The analysis of overrepresented sequences will spot an increase in any exactly duplicated sequences, but there are a different subset of problems where it will not work.
\t- If you have very long sequences with poor sequence quality then random sequencing
\t  errors will dramatically reduce the counts for exactly duplicated sequences.
\t- If you have a partial sequence which is appearing at a variety of places within
\t  your sequence then this won't be seen either by the per base content plot or
\t  the duplicate sequence analysis.

The Kmer module starts from the assumption that any small fragment of sequence should not have a positional bias in its apearance within a diverse library. There may be biological reasons why certain Kmers are enriched or depleted overall, but these biases should affect all positions within a sequence equally. This module therefore measures the number of each 7-mer at each position in your library and then uses a binomial test to look for significant deviations from an even coverage at all positions. Any Kmers with positionally biased enrichment are reported. The top 6 most biased Kmer are additionally plotted to show their distribution.
To allow this module to run in a reasonable time only 2% of the whole library is analysed and the results are extrapolated to the rest of the library. Sequences longer than 500bp are truncated to 500bp for this analysis.

*Warning*
This module will issue a warning if any k-mer is imbalanced with a binomial p-value <0.01.

*Failure*
This module will issue a warning if any k-mer is imbalanced with a binomial p-value < 10^-5.

*Common reasons for warnings*
Any individually overrepresented sequences, even if not present at a high enough threshold to trigger the overrepresented sequences module will cause the Kmers from those sequences to be highly enriched in this module. These will normally appear as sharp spikes of enrichemnt at a single point in the sequence, rather than a progressive or broad enrichment.
Libraries which derive from random priming will nearly always show Kmer bias at the start of the library due to an incomplete sampling of the possible random primers.
        """,
        # Basic statistics
        "basic_statistics":
        """
== Basic Statistics ==
(Link: http://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/1%20Basic%20Statistics.html)

*Summary*
The Basic Statistics module generates some simple composition statistics for the file analysed.
\t- Filename: The original filename of the file which was analysed
\t- File type: Says whether the file appeared to contain actual base
\t  calls or colorspace data which had to be converted to base calls
\t- Encoding: Says which ASCII encoding of quality values was found
\t  in this file.
\t- Total Sequences: A count of the total number of sequences processed.
\t  There are two values reported, actual and estimated. At the moment
\t  these will always be the same. In the future it may be possible to
\t  analyse just a subset of sequences and estimate the total number,
\t  to speed up the analysis, but since we have found that problematic
\t  sequences are not evenly distributed through a file we have disabled
\t  this for now.
\t- Filtered Sequences: If running in Casava mode sequences flagged to
\t  be filtered will be removed from all analyses. The number of such
\t  sequences removed will be reported here. The total sequences count
\t  above will not include these filtered sequences and will the number
\t  of sequences actually used for the rest of the analysis.
\t- Sequence Length: Provides the length of the shortest and longest
\t  sequence in the set. If all sequences are the same length only
\t  one value is reported.
\t- %GC: The overall %GC of all bases in all sequences

*Warning*
Basic Statistics never raises a warning.

*Failure*
Basic Statistics never raises an error.

*Common reasons for warnings*
This module never raises warnings or errors
        """,
        # Adapter content
        "adapter_content":
        """
== Adapter Content ==
(Link: http://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/10%20Adapter%20Content.html)

*Summary*
The Kmer Content module will do a generic analysis of all of the Kmers in your library to find those which do not have even coverage through the length of your reads. This can find a number of different sources of bias in the library which can include the presence of read-through adapter sequences building up on the end of your sequences.
You can however find that the presence of any overrepresented sequences in your library (such as adapter dimers) will cause the Kmer plot to be dominated by the Kmers these sequences contain, and that it's not always easy to see if there are other biases present in which you might be interested.
One obvious class of sequences which you might want to analyse are adapter sequences. It is useful to know if your library contains a significant amount of adapter in order to be able to assess whether you need to adapter trim or not. Although the Kmer analysis can theoretically spot this kind of contamination it isn't always clear. This module therefore does a specific search for a set of separately defined Kmers and will give you a view of the total proportion of your library which contain these Kmers. A results trace will always be generated for all of the sequences present in the adapter config file so you can see the adapter content of your library, even if it's low.
The plot itself shows a cumulative percentage count of the proportion of your library which has seen each of the adapter sequences at each position. Once a sequence has been seen in a read it is counted as being present right through to the end of the read so the percentages you see will only increase as the read length goes on.

*Warning*
This module will issue a warning if any sequence is present in more than 5% of all reads.

*Failure*
This module will issue a warning if any sequence is present in more than 10% of all reads.

*Common reasons for warnings*
Any library where a reasonable proportion of the insert sizes are shorter than the read length will trigger this module. This doesn't indicate a problem as such - just that the sequences will need to be adapter trimmed before proceeding with any downstream analysis.
        """,
        # Overrepresented sequences
        "overrepresented_sequences":
        """
== Overrepresented Sequences ==
(Link: http://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/9%20Overrepresented%20Sequences.html)

*Summary*
A normal high-throughput library will contain a diverse set of sequences, with no individual sequence making up a tiny fraction of the whole. Finding that a single sequence is very overrepresented in the set either means that it is highly biologically significant, or indicates that the library is contaminated, or not as diverse as you expected.
This module lists all of the sequence which make up more than 0.1% of the total. To conserve memory only sequences which appear in the first 100,000 sequences are tracked to the end of the file. It is therefore possible that a sequence which is overrepresented but doesn't appear at the start of the file for some reason could be missed by this module.
For each overrepresented sequence the program will look for matches in a database of common contaminants and will report the best hit it finds. Hits must be at least 20bp in length and have no more than 1 mismatch. Finding a hit doesn't necessarily mean that this is the source of the contamination, but may point you in the right direction. It's also worth pointing out that many adapter sequences are very similar to each other so you may get a hit reported which isn't technically correct, but which has very similar sequence to the actual match.
Because the duplication detection requires an exact sequence match over the whole length of the sequence any reads over 75bp in length are truncated to 50bp for the purposes of this analysis. Even so, longer reads are more likely to contain sequencing errors which will artificially increase the observed diversity and will tend to underrepresent highly duplicated sequences.

*Warning*
This module will issue a warning if any sequence is found to represent more than 0.1% of the total.

*Failure*
This module will issue an error if any sequence is found to represent more than 1% of the total.

*Common reasons for warnings*
This module will often be triggered when used to analyse small RNA libraries where sequences are not subjected to random fragmentation, and the same sequence may natrually be present in a significant proportion of the library.
        """,
        # Per base N content
        "per_base_n_content":
        """
== Per Base N Content ==
(Link: http://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/6%20Per%20Base%20N%20Content.html)

*Summary*
If a sequencer is unable to make a base call with sufficient confidence then it will normally substitute an N rather than a conventional base] call
This module plots out the percentage of base calls at each position for which an N was called.
It's not unusual to see a very low proportion of Ns appearing in a sequence, especially nearer the end of a sequence. However, if this proportion rises above a few percent it suggests that the analysis pipeline was unable to interpret the data well enough to make valid base calls.

*Warning*
This module raises a warning if any position shows an N content of >5%.

*Failure*
This module will raise an error if any position shows an N content of >20%.

*Common reasons for warnings*
The most common reason for the inclusion of significant proportions of Ns is a general loss of quality, so the results of this module should be evaluated in concert with those of the various quality modules. You should check the coverage of a specific bin, since it's possible that the last bin in this analysis could contain very few sequences, and an error could be prematurely triggered in this case.
Another common scenario is the incidence of a high proportions of N at a small number of positions early in the library, against a background of generally good quality. Such deviations can occur when you have very biased sequence composition in the library to the point that base callers can become confused and make poor calls. This type of problem will be apparent when looking at the per-base sequence content results.
        """,
        # Per sequence quality scores
        "per_sequence_quality_scores":
        """
== Per Sequence Quality Scores ==
(Link: http://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/3%20Per%20Sequence%20Quality%20Scores.html)

*Summary*
The per sequence quality score report allows you to see if a subset of your sequences have universally low quality values. It is often the case that a subset of sequences will have universally poor quality, often because they are poorly imaged (on the edge of the field of view etc), however these should represent only a small percentage of the total sequences.
If a significant proportion of the sequences in a run have overall low quality then this could indicate some kind of systematic problem - possibly with just part of the run (for example one end of a flowcell).
Results from this module will not be displayed if your input is a BAM/SAM file in which quality scores have not been recorded.

*Warning*
A warning is raised if the most frequently observed mean quality is below 27 - this equates to a 0.2% error rate.

*Failure*
An error is raised if the most frequently observed mean quality is below 20 - this equates to a 1% error rate.

*Common reasons for warnings*
This module is generally fairly robust and errors here usually indicate a general loss of quality within a run. For long runs this may be alleviated through quality trimming. If a bi-modal, or complex distribution is seen then the results should be evaluated in concert with the per-tile qualities (if available) since this might indicate the reason for the loss in quality of a subset of sequences.
        """
}


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
    """
    Reads samples directories and creates objects for each sample.
    """
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
    print "print_module_description           - prints textual description of given module"


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

    # Supported commands for auto-completion
    supported_start_commands = [
        "help",
        "exit",
        "open_sample_html_report",
        "print_global_stats",
        "print_module_stats",
        "print_sample_details",
        "print_samples_by_status_in_module",
        "print_all_samples_orderby_status",
        "print_all_modules_orderby_status",
        "print_module_description",
    ]

    # Supported module-names for auto-completion
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

    # Supported statuses for auto-completion
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
                print "BLEEP BLOP, DOES NOT COMPUTE! INVALID STATUS NAME: %s" % status_name
                continue

            # Print samples ordered by status
            sample_manager.print_samples_orderby_status(status_name)
            continue

        # Print module descriptions
        if choice.startswith("print_module_description"):
            # Setup auto-completer for module name
            completer = MyCompleter(supported_module_names)
            readline.set_completer(completer.complete)
            readline.parse_and_bind('tab: complete')

            # Read module name
            module_name = raw_input(">> Module name: ")

            # Validate
            if module_name not in supported_module_names:
                print "BLEEP BLOP, DOES NOT COMPUTE! INVALID MODULE NAME: %s" % module_name
                continue

            # Print module description
            print "================ MODULE DESCRIPTION ================"
            print module_descriptions[module_name]


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
