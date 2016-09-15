# fastqc-browser
A command-line based tool to browse FastQC output. Written in Python 2.7.

## Usage
```python fastqc_browser.py -i fastq_output_dir/```

FastQC-browser takes a single argument ```-i/--input-directory```, which is a directory containing output from FastQC with a structure like the following tree:
```
-fastqc_output_dir/
  |-- sample1/
      |-- sample1_1.zip
      |-- sample1_2.zip
      |-- report.html
  |-- sample2/
      |-- sample2_1.zip
      |-- sample2_2.zip
      |-- report.html
  |-- sample3/
      |-- sample3_1.zip
      |-- sample3_2.zip
      |-- report.html
```

## Supported commands
Supported commands are:
* **help** - Prints available commands
* **exit** - Quits the program
* **open_sample_html_report** - Open HTML report in browser (if available)
* **print_global_stats** - Prints total number of PASS/WARN/FAILs
* **print_module_stats** - Prints stats (PASS/WARN/FAIL) per module 
* **print_sample_details** - Prints stats for a given sample
* **print_samples_by_status_in_module** - Prints the samples that PASS/WARN/FAIL a given module
* **print_all_samples_orderby_status** - Prints all samples ordered by PASS/WARN/FAILs
* **print_all_modules_orderby_status** - Prints all modules ordered by PASS/WARN/FAILs
* **print_module_description** - Prints textual description of given module

Press **TAB** (sometimes twice) to see every available command in the current context. **TAB** also autocompletes to supported commands.

## Examples
* Print an overview of all the modules:
```
> print_module_stats

===========================================================================
=============================== MODULE STATS ==============================
===========================================================================
MODULE                          PASS	 WARN	 FAIL
Adapter Content                  162	   98	    0
Basic Statistics                 260	    0	    0
Kmer Content                       0	    0	  260
Overrepresented sequences          0	  259	    1
Per base N content               260	    0	    0
Per base sequence content          0	    1	  259
Per base sequence quality        260	    0	    0
Per sequence GC content            8	   96	  156
Per sequence quality scores      260	    0	    0
Per tile sequence quality        238	   22	    0
Sequence Duplication Levels        0	   31	  229
Sequence Length Distribution     192	   68	    0
```
* List the sample that failed module *Overrepresented sequences*:
```
> print_samples_by_status_in_module
>> Module name: overrepresented_sequences
>>> Status: FAIL

SAMPLE NAME                   MODULE NAME                   STATUS    FASTQ(s)
sample73                      Overrepresented sequences      FAIL        1 
```
* Print details of sample73
```
> print_sample_details
>> Sample name: sample73

==========================================================================================
===================================== SAMPLE DETAILS =====================================
==========================================================================================
SAMPLE NAME                         PASS           WARN           FAIL     
sample73                        14 (58.33%)     1 (4.17%)      9 (37.50%)  

================================= FASTQC DATA - FASTQ #1==================================
INFO                                    VALUE                                             
Sequences flagged as poor quality       0                                                 
Encoding                                Sanger / Illumina 1.9                             
Sequence length                         101                                               
File type                               Conventional base calls                           
Total Sequences                         39996006                                          
%GC                                     50                                                
Filename                                73_R1_001.fastq                                   

================================= FASTQC DATA - FASTQ #2==================================
INFO                                    VALUE                                             
Sequences flagged as poor quality       0                                                 
Encoding                                Sanger / Illumina 1.9                             
Sequence length                         101                                               
File type                               Conventional base calls                           
Total Sequences                         39996006                                          
%GC                                     51                                                
Filename                                73_R2_001.fastq                                   

======================================== MODULES =========================================
NAME                                              FASTQ #1  FASTQ #2  
Adapter Content                                      PASS      PASS   
Basic Statistics                                     PASS      PASS   
Kmer Content                                         FAIL      FAIL   
Overrepresented sequences                            FAIL      WARN   
Per base N content                                   PASS      PASS   
Per base sequence content                            FAIL      FAIL   
Per base sequence quality                            PASS      PASS   
Per sequence GC content                              FAIL      FAIL   
Per sequence quality scores                          PASS      PASS   
Per tile sequence quality                            PASS      PASS   
Sequence Duplication Levels                          FAIL      FAIL   
Sequence Length Distribution                         PASS      PASS
```
* Open HTML report for FASTQ #1 in sample73 to check out the plots:
```
> open_sample_html_report
>> Sample name: sample73
>>> Read file number: 1
*opens report in webbrowser*
```
* **NOTE:** TAB auto-completion is your friend!
```
> print_module_d<TAB>
> print_module_description <ENTER>
>> Module name: ov<TAB>
>> Module name: overrepresented_sequences <ENTER>
...
```

## Compatibility
### Python 2
It's written in Python 2.7. Python 2.6 seems to have issues with string formatting.
### Python 3
Experimental testing suggests Python 3 compatibility is easily achieved. Convert to Python 3 using ```2to3```:

```2to3 -w *.py```

Execute using Python 3:

```python3 fastqc_browser.py -i fastqc_output_dir```



