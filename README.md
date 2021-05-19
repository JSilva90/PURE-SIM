
# PURE-SIM

 This script implements the PURE-SIM (PUblication Relatedness Estimator using Star-schema Information networks of Metadata) algorithm in Python. The PURE-SIM algorithm can be used to estimate publications similarities using any metadata relations available. For more details about the PURE-SIM algorithm please refer to [1]. This implementation reads the data from JSON file where each line represents a publication and the different metadata associated with it (example bellow). Following the PURE-SIM specifications we added an argument "-M" which allows the user to select the metadata information used to compute publications similarities. Based on the metadata selected, this implementation creates an HIN (Heterogeneous Information Network) with the publications and the selected metadata that is shared by one or more publications (i.e., if keyword k1 is used in two publications p1 and p2 the edges p1-k1 and p2-k1 exist the in HIN). Next, this implementation computes the transaction probabilities between publications. This is step is not part of the PURE-SIM algorithm but it is a strategy used to reduce the time complexity of computing the random walks. Finally, the transaction probabilities are used to simulate N (user-defined parameter) random walks per publication which are used to estimate the publications similarities. The end result is written to a file specified by the user. 
For more details about the PURE-SIM algorithm and an extensive study of the best metadata to use, please refer to [1]. 

## Data 

This implementation reads the data from a JSON file. Each line of the JSON file is a publication and its metadata separated by categories or groups. Here is an example of a line from the JSON file (a sample dataset is provided in this repository)-

{"id": 1572886, "journals": [18400], "keywords": ["Overweight/obese", "Type 2 diabetes", "Lifestyle weight-loss interventions"], "couplingCitations": ["000306122600006", "000312909000002", "000296181800004"], "references": ["15728860000002512763", "15728860000002078659", "15728860000002565938", "15728860000002695938", "15728860000002845237"], "authors": [12528582, 11170365, 18742992, 32035541]}

In this example there are 5 categories of metadata for this publication: journals, keywords, couplingCitations, references and authors. This implementation does not implement any data pre-processing step and assumes that each metadata is an id for that metadata attribute. According to PURE-SIM publication this is trivial for metadata categories such as authors, keywords and journals. However, for citation information it is necessary to create *fictional* data. For example, in the data provided as example, the references are an id of two publications and a *000000* padding between them. Furthermore, the coupling citations are an id that represents the action of citing some publication. For more details about this, please refer to the PURE-SIM paper [1].

This implementations discards metadata attributes from the data that are not shared by more than one publication and removes publications that are isolated from all the others (i.e., there is no path in the HIN for that publication to any other.) The number of metadata attributes and publications removed from the dataset is provided as output of this implmentation. Here's an example bellow:

> Number of nodes removed per type:
> {'J': 260, 'R': 1023, 'C': 25406, 'K': 3375, 'A': 5755}
> Removed 90 nodes because they are isolated
> Number of nodes per type in the network:
> {'P': 910, 'C': 555, 'K': 296, 'A': 38, 'R': 2, 'J': 205}

Note that this implementation only considers the first letter of the metadata categories (e.g., K = keywords) to identify different types of nodes. P is always the letter associated with the publication nodes.

## Output

This implementation outputs a file where each line consists of the two publications ids and their estimated similarity. Here is an example:

> P_1049873 P_1049084 0.295918
> P_1049873 P_1049957 0.096939
> P_1049873 P_1049962 0.102041
> P_1049873 P_1049954 0.112245


## User-defined parameters

This implementation uses the following arguments for the script:

* `data` used to specify the path to the input file.
* `M` used to select the metadata categories to read from the input file. Each group should be separated by "\_" (e.g. authors\_keywords).
* `N` defines the number of random walks per publication.
* `W` defines the weighting scheme used. There are two available: _metadata_ and _publication_.
* `cpus` defines the number of cpus to use
* `outfile` defines the name of the file where the similarities are written.

## Usage

In this repository we provide a sample dataset to test this PURE-SIM implementation. Using this dataset as an example, to run the PURE-SIM algorithm with 300 random walks per publication, the metadata weighting scheme, 4 cpus and the similarities being computed considering the metadata categories of authors, keywords, journals, coupling citations and references. The following line should be used:

`python PURESIM.py -data sample_dataset.JSON -M authors_keywords_journals_couplingCitations_references -W metadata -N 300 -cpus 4 -outfile test_sims.csv `

## Experiments

In this repository we also provide more results for the experiments conducted in [1]. We consider this information valuable to anyone that is considering using the PURE-SIM algorithm since they provided a detailed analysis of the best parameters to use in the algorithm. For these experiments publications with a print year in the period 2013--2017 from the PubMed dataset. Furthermore, we used the [Leiden algorithm](https://github.com/vtraag/leidenalg) to cluster the publications based on the produced similarities.

The plots are in the _PublicationResults_ folder and are organized as follows:

* `D10\_n\_parameter` a folder that contains the GA plots for all the metadata combinations the results of changing the _N_ parameter in the D10 dataset.
* `D10\_w\_parameter` a folder that contains the GA plots for all the metadata combinations the results of changing the _W_ parameter in the D10 dataset.
* `D20\_m\_parameter` a folder that contains the GA plots for the results of changing the _M_ parameter in the D20 dataset with a fixed _N_ = 300 and _W_ = metadata.
* `D20\_m\_combinations_gains` a folder that contains the GA plots of groups of metadata combinations that contain or not a certain metadata category (e.g., the Author file has a GA line which represents the average GA line for all the metadata combinations that do not use authors and another GA line which represents the average GA line for all the metadata combinations that use authors.)
* `D20\_all\_m\parameter_` a single image with the GA plot for all metadata combinations in the D20 dataset.
* `D20\_m\_parameter` a single GA plot with some metadata combinations in the D20 dataset.
* `D20\_best\_m\_parameter` a single GA plot with the best metadata combinations in the D20 dataset.


## References

Please cite the references appropriately in case they are used.

[1] Jorge Silva, Nees Jan van Eck, Pedro Ribeiro, Fernando Silva (2021). PURE-SIM: exploring metadata relations to estimate publication similarity. Soon to appear.