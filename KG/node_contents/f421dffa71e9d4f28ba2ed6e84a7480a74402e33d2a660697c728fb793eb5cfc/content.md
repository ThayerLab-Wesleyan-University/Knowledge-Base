## Page 1

Bioinformatics,                                                                                      2025,    41(9),                             btaf420
https://doi.org/10.1093/bioinformatics/btaf420
Advance   Access  Publication   Date:  31  July  2025
Original     Paper


Structural    bioinformatics
MDGraphEmb: a toolkit for graph embedding and
classification of protein conformational ensembles
Ferdoos Hossein Nezhad1,�                            , Namir Oues1                , Massimiliano Meli2                     , Alessandro Pandini1,3,�

1Department  of Computer Science, Brunel University of London, Uxbridge UB8 3PH,  United Kingdom
2Istituto di Scienze e Tecnologie Chimiche  “Giulio Natta”—SCITEC, Consiglio Nazionale delle Ricerche, Milano 20131, Italy
3The Thomas Young Centre  for Theory and Simulation  of Materials, London SW7 2AZ, United Kingdom
�Corresponding  authors. Ferdoos  Hossein  Nezhad,  Department  of Computer  Science,  Brunel  University  of London,  Kingston  Lane,  UB8  3PH,  Uxbridge,  United
Kingdom.  E-mail: Ferdoos.HosseinNezhad@brunel.ac.uk;  Alessandro  Pandini,  Department  of Computer  Science,  Brunel  University  of London,  Kingston  Lane, UB8
3PH,  Uxbridge,  United  Kingdom.  E-mail: alessandro.pandini@brunel.ac.uk.
Associate Editor: Jianlin Cheng
Abstract
Motivation: Molecular Dynamics (MD) simulations are essential for investigating protein dynamics and function. Although significant advances
have been made in integrating simulation techniques and machine learning, there are still challenges in selecting the most suitable data repre-
sentation   for   learning.   Graph   embedding   is   a   powerful   computational   method   that   automatically   learns   low-dimensional   representations   of
nodes in a graph while preserving graph topology and node properties, thereby bridging graph structures and machine learning methods. Graph
embeddings hold great potential for efficiently representing MD simulation data and studying protein dynamics.
Results:  We  present  MDGraphEmb,  a  Python  library  built  on  MDAnalysis,  specifically  designed  to  convert  protein  MD  simulation  trajectories
into   graph-based   representations   and   corresponding   graph   embeddings.   This  transformation   enables   the  compression   of   high-dimensional,
noisy trajectories from protein simulations into tabular formats suitable for machine learning. MDGraphEmb provides a framework that supports
a range of graph embedding techniques and machine learning models, enabling the creation of workflows to analyse protein dynamics and iden-
tify important protein conformations. Graph embedding effectively captures and compresses structural information from protein MD simulation
data,  making  it  applicable  to  diverse  downstream  machine-learning  classification  tasks.  We  present  an  application  for  encoding  and  detecting
important  protein  conformations  from  molecular  dynamics  simulations  to  classify  functional  states,  using  adenylate  kinase  (ADK)  as  the  main
case study. To assess the generalizability of the approach, two additional systems, Plantaricin E (PlnE) and HIV-1 protease are included as sup-
plementary validation examples. A performance comparison of different graph embedding methods combined with machine learning models is
also provided.
Availability and implementation: MDGraphEMB GitHub Repository: https://github.com/FerdoosHN/MDGraphEMB.


1 Introduction                                                                                Recently,    machine    learning    techniques    have    demonstrated
Proteins are  at  the core  of  most  biological  processes.  Their  abil-                    great potential for analysing and extracting insights from the
ity  to  adopt  different  conformations  is  essential  for  several  bio-                   extensive  data  generated  by  MD  simulations  (Glielmo   et   al.
logical processes, including enzymatic activity, signalling, genetic                          2021,    Kaptan   and   Vattulainen   2022,              Hagg   and   Kirschner
information   processing,   transport   and   trafficking,   immune   re-                     2023).     However,     molecular     simulation     data,     particularly
sponse, and cellular homeostasis mechanisms. Investigating these                              in    the    case    of    atomistic    molecular    dynamics,    has    a    low
processes often requires identifying important protein conforma-                              signal-to-noise  ratio,  making  the  detection  and  modelling  of
tions associated with functional states and describing the mecha-                             functionally relevant motions challenging. As a result, dimen-
nisms of transition between these states.                                                     sionality   reduction   and   data   compression   are    increasingly
   In this regard, MD simulations have become a routine tool                                  used  for  extracting  biologically  meaningful  patterns  and  en-
for studying protein dynamics and exploring their conforma-                                   abling  efficient,  quantitative  interpretation  through  machine
tional space (Henzler-Wildman and Kern 2007). These simu-                                     learning.  Historically,  unsupervised  machine  learning  meth-
lations    provide    information    on    events    at    the    atomic    and               ods  have  been  used  to  extract  meaningful  information  from
molecular   levels,   capturing   processes   up   to   the   millisecond                     conformational  landscapes,  particularly  through  dimension-
scale.   Moreover,   MD   simulation   techniques   are   frequently                          ality  reduction  (Glielmo    et    al.  2021).  Approaches  based  on
used  in  combination  with  experimental  methods  to  investi-                              machine and deep learning have been developed to handle di-
gate  functional  dynamics  in  proteins.  Similar  to  other  areas                          mensionality  reduction  and  compress  information  from  MD
of  data-driven  research,  the  availability  of  faster  algorithms                         simulation   data,   facilitating   effective   learning   (Lemke   and
and   high-performance   parallelization   has   made   it   easier   to                      Peter   2019,     Lemke      et      al.   2019).   Recently,   an   autoencoder
study  more  complex  problems  over  extended  timescales,  of-                              (Jin   et   al.  2021)  was  used  to  map  MD  simulation  snapshots
ten  approaching  those  observed  in  experimental  techniques.                              to        a        conformational        landscape        defined        by        principal


Received: 14 February 2025; Revised: 12 June 2025; Editorial Decision: 27 June 2025; Accepted: 28 July 2025
© The Author(s) 2025. Published by Oxford University Press.
This is an Open Access article distributed under the terms of the Creative Commons Attribution License (https://creativecommons.org/licenses/by/4.0/),                                                                                                                                               which
permits unrestricted reuse, distribution, and reproduction in any medium, provided the original work is properly cited.

## Page 2

2                                                                                                                                                                                                                  Hossein Nezhad et al.

component  analysis,  enabling  the  prediction  of  new  confor-                          comprehensive   survey   on   graph   embedding   techniques   and
mations not included in the training data.                                                 graph    representation    learning    in    bioinformatics,    detailing
   While  dimensionality  reduction  methods  can  enhance  fea-                           trends, methods, and applications, can be found in Wu  et  al.
ture  extraction,  they  require  a  thorough  analysis  of  the  con-                     (2023)    and Yi et al. (2022). In recent years, graph embedding
formational         space.         Alternative         approaches         focus         on and graph learning techniques have been increasingly applied
modifying  the  data  representation  of  each  conformation  to                           to  predict  protein  function  by  leveraging  information  from
generate  more  informative  representations  of  key  degrees  of                         protein  sequences,  structures,  and  interaction  networks  (Lin
freedom  and  their  relationships.  In  this  context,  the  spatial                      et al. 2024, Boadu et al. 2025). However, these methods have
arrangement  and  interactions  of  protein  residues  have  been                          yet to be thoroughly tested or analysed in the context of pro-
effectively represented using graph models (Patel et al. 2024).                            tein dynamics and MD simulation data.
These  models  have  been  particularly  successful  in  capturing                            In  this  paper,  we  explore  graph  embedding  as  an  effective
the   multiscale   nature   of   intrinsic   dynamics   and   conforma-                    computational method for learning low-dimensional node rep-
tional   motions,   accurately   modelling   both   global   and   local                   resentations of ensembles of protein structure graphs from mo-
changes, as well as complex time-resolved events such as allo-                             lecular  dynamics.  To  this  end,  we  developed  MDGraphEmb,
steric communication.                                                                      an      object-oriented      Python      library      built      on      top      of      the
   Graph  representations  have  been  used  successfully  to  en-                         MDAnalysis   library   (Michaud-Agrawal      et      al.   2011,          Gowers
code   and   analyse   the   conformational   properties   of   protein                    et   al.  2019).  MDGraphEmb  facilitates  the  conversion  of  MD
structures  (Patel    et    al.  2024).  For  residue-based  representa-                   simulation data from protein conformations  into graph repre-
tions,  a  single  graph  was  typically  constructed  from  average                       sentations and then into graph embeddings using different em-
information    on    residue-residue    interactions    or    dynamical                    bedding  methods.  The  tool  also  supports  a  range  of  machine
coupling, given an ensemble of conformations. An alternative                               learning  and  deep  learning  models  to  create  predictors  of  im-
approach  involves  encoding  the  ensemble  as  a  collection  of                         portant  protein  conformations  from MD  simulation  data.  We
graphs.    However,    the    heterogeneity    and    dynamic    nature                    demonstrate  that  graph  embedding  effectively  captures  struc-
of conformational ensembles, combined with the complexity                                  tural information from MD simulation data, making it suitable
of   high-dimensional   data,   present   significant   challenges  for                    for different machine learning classification tasks. An example
traditional graph analysis.                                                                application   using   the   ADK   protein   system   is   presented   for
   Graph  embedding  techniques  address  these  challenges  by                            encoding and detecting important protein conformations from
converting graph data into low-dimensional vector represen-                                molecular   dynamics   simulations   to   classify   functional   states.
tations while preserving key structural information, enabling                              Within  this  context,  we  compare  the  performance  of  various
more  efficient  and  effective  analysis.  In  addition,  graph  em-                      graph embedding methods in combination with machine learn-
bedding   techniques   offer   significant   computational   advan-                        ing    models    to    evaluate    their    effectiveness.    Based    on    these
tages    over    methods    that    operate    directly    on    the    original           results, we recommend the most effective embedding and clas-
networks. They facilitate faster processing and can be used to                             sification   strategies.   To   assess   the   generalizability   of   the   ap-
build  machine  learning  models  for  various  predictive  tasks,                         proach, two additional systems (PlnE and HIV-1 protease) are
such  as  node  classification,  community  detection,  clustering,                        included as supplementary validation examples.
and   visualization   (Hamilton     et     al.   2017, Yue     et     al.   2020).            Conformational  states  are  often  identified  using  unsuper-
Additionally,  working in  a  lower-dimensional space  helps to                            vised  learning  methods  such  as  clustering  analysis.  While  ef-
manage   noise   present   in   the   original   network   more   effec-                   fective   as   an   exploratory   analysis   tool,   clustering   relies   on
tively. Modelling using the graph embedding developed in re-                               similarity-based  grouping  and  often  struggles  to  distinguish
cent years (Grover and Leskovec 2016, Hamilton et al. 2017,                                continuous  transitions  between  conformational  states,  espe-
Zhang  et  al. 2018, Cui  et  al. 2019, Yue  et  al. 2020). In gen-                        cially   in   complex,   high-dimensional   datasets.   Moreover,   it
eral, graph embedding methods can be categorized into three                                typically requires ad-hoc parameter selection, and the result-
main  types:  spectral-based,  random  walk-based,  and  neural                            ing groupings are not directly transferable to new simulation
network-based    methods    (Nelson         et         al.    2019,  Yue         et         al. data.    The    supervised    learning    approach    presented    in    this
2020). The field of graph learning has expanded significantly,                             study offers a way to overcome these limitations and comple-
progressing beyond traditional graph representation learning                               ment  clustering.  If  representative  state  labels  can  be  derived
and      neural      network-based      embedding      techniques.      This               from  one  simulation,  the  trained  model  can  then  be  used  to
growth has driven the development and evaluation of various                                predict conformational states in new, unseen datasets.
Graph      Neural     Network      (GNN)      architectures,      including                   While graph learning frameworks such as PyG and DGL of-
Graph    Convolutional    Network    (GCN)    (Kipf    and    Welling                      fer extensive support for implementing graph neural networks
2017),         Graph         Sample         and         Aggregate         (GraphSAGE)      and embedding  techniques, they  are general-purpose  libraries
(Hamilton et al. 2017), and Graph Attention Network (GAT)                                  not  specifically  optimized  for  the  unique  challenges  posed  by
(Veli�ckovi�c      et      al.   2020),   each   designed   to   address   specific        MD  simulation  data.  In  contrast,  MDGraphEmb  is  an  open-
challenges in graph-based tasks. These models have been suc-                               source   library   specifically   developed   to   provide   a   domain-
cessfully  applied  to  a  wide range  of  applications (Zitnik  and                       specific     workflow     for     analysing     protein     MD     simulations
Leskovec 2017, Jin  et  al.  2018, You  et  al. 2018).  Moreover,                          through graph-based learning. It integrates widely used meth-
platforms such as GraphGym and PyTorch Geometric (PyG)                                     ods    (including    Node2Vec,    GCN,    GAT,    and    GraphSAGE)
(Fey  and  Lenssen  2019,          You     et     al.  2020)  have  emerged  as            within      a      unified      framework      that      operates      directly      on
powerful     tools     for     exploring     and     benchmarking     various              MDAnalysis-compatible        trajectory         data.         MDGraphEmb
GNN   architectures   and   tasks.   Deep   Graph   Library   (DGL)                        streamlines  the  entire  process,  from  trajectory  preprocessing
(Wang et  al. 2020b) complements these efforts with a graph-                               and graph construction to representation learning and down-
centric   design   that   supports   efficient   parallel   computation                    stream   classification,   enabling   domain   experts   in   computa-
through            generalized            sparse            tensor            operations.            A tional biology to apply graph learning without requiring deep

## Page 3

MDGraphEmb                                                                                                                                                                                                                                3

expertise in graph neural network programming. It also offers                                        The      resulting       graphs       are      then      embedded       using       the
pre-configured workflows, protein-specific graph construction                                     PyTorch Geometric package   (Fig.   2b).   Users   can   select
routines, and seamless pipelines for embedding and classifica-                                    from   different   embedding   methods   or   configure   their   own
tion, along with built-in tools for benchmarking and compar-                                      hyperparameters.     Both    random    walk-based     methods     (e.g.
ative evaluation.                                                                                 node2vec)                                                    and        neural        network-based        methods        (e.g.
                                                                                                  GraphSAGE,                                                                                      GAT,                              GCN)                  are  supported.  The  embedding  gen-
2 Materials and methods                                                                           erates    a    lower-dimensional    representation    of    the    protein’s
2.1 Python library architecture                                                                   trajectory space (Fig. 2c). The embedding output is a series of
                                                                                                  matrices  with  dimensions   jV   j    × jdj,            where  jV   j    represents   the
MDGraphEmb is an object-oriented  Python library for analy-                                       number  of  nodes  in  the  graph  (equivalent   to  the  number  of
sing protein dynamics using graph embeddings.  Library func-                                      Cα)             and jdj          represents the dimension of the embedded vectors
tions  are included  to: (i) convert  protein  conformations  from                                for each  frame.  Since  there  are  n frames  in the trajectory,  we
MD     trajectories     into     graph     representations;     (ii)     generate                 obtain     n  matrices   of  size   jV   j    × jdj.             The   matrix   output   from
graph   embeddings    using   well-established    embedding   meth-                               the embedding  model is reshaped for each frame into a single
ods;  and (iii)  train  machine  and deep  learning  models  to pre-                              vector   of  size  jV   j    × jdj,            effectively   mapping   the  entire  graph
dict     functional     properties     of     protein     conformations.     The                  for  one  frame  to  a  single  vector.  The  trajectory  data  is  com-
library   was   built   on   top   of   MDAnalysis    and   incorporates                          pressed into a tabular format conveniently  processed by most
functions   from   NetworkX   (Hagberg      et      al.   2008),   PyTorch                        machine   learning   algorithms.   If   an   example   of   a   per-frame
Geometric  (Fey and Lenssen 2019), TensorFlow  (Abadi  et al.                                     property   of   interest   is   available,   a   predictive   model   can   be
2016),  and  scikit-learn   (Pedregosa     et    al.  2011).  At  its  core,                      trained using supervised learning methods. Parameter settings
MDGraphEmb  provides  a flexible  set  of  classes  for  handling                                 for  the  graph  embedding  methods  and  configurations  of  the
protein   conformations   using   three   different   representations:                            machine  learning  models  are  provided  in  the Supplementary
Protein,                                         ProteinGraph,                                                       and ProteinEmb.Materials(Methods:        Architectures        of        the        Embedding
   The  Protein  class  uses  the  MDAnalysis  Universe  to  repre-                               Methods      and     Machine      Learning      Models               Supplementary
sent  Cartesian   and  topological   information   on  protein   con-                             Materials),             available              as supplementary              data       at
formations   extracted   from   MD   trajectory   files,   following   a                          Bioinformatics online.
previous   class  design   (Oues     et    al.  2023).  The   ProteinGraph                           This toolkit supports a variety of supervised machine learn-
class  converts  these  protein  conformations   into  graphs,  pre-                              ing algorithms through scikit-learn and TensorFlow (Fig. 2d),
serving    the   spatial    relationships    between    atoms   in   protein                      including neural networks (NN), (CNN), and boosting meth-
data.  In  more  detail,  for  each  frame,  the  self-distance   array                           ods like LightGBM  (LGBM) and XGBoost  (XGB), which are
from MDAnalysis is converted into a weighted adjacency ma-                                        well  suited  to high-dimensional  data.  Additionally,  it accom-
trix,  and  a  graph  is  generated  using  NetworkX.  A  cut-off  is                             modates  traditional  machine  learning  techniques  such  as  lo-
applied  to the adjacency  matrix  to filter  contact  connections.                               gistic       regression,       random       forests,       and       support       vector
Through  this  process,  the  MD  trajectory  is  converted  into  a                              machines.  The toolkit provides  a comprehensive  graph learn-
series of graphs. The ProteinEmb class compresses each graph                                      ing framework encompassing the entire process, from embed-
into   an   embedding.   It   supports   different   graph   embedding                            ded protein data to target processing, classification  reporting,
methods     to     transform     high-dimensional     graph     data     into                     visualization,  and performance comparison between different
lower-dimensional        embeddings.        This       process       not       only               embedding methods and machine learning models.
reduces computational  complexity  but also allows for the ex-                                    2.3 Case study: system description
traction  of  meaningful  features  that  are  critical  for  machine
learning     tasks.     To     this     end,     the     library     also     includes     a      Adenylate   kinase   (ADK)   is  an  enzyme   within   the  phospho-
ProteinTarget    class,    which    can    record    per-frame    (i.e.    per-                   transferase family, playing a central role in maintaining cellu-
graph)   target   properties   to  predict.   A   ML  class   is  provided                        lar   energy   balance   by   catalysing   the   conversion   of   adenine
for  convenience,  which  offers  direct  access  to  various  super-                             nucleotides.  A  critical  step  in  the  catalytic  cycle  is  the  transi-
vised  learning  algorithms.  These  algorithms,  alongside  evalu-                               tion between an open and a closed state. This conformational
ation    methods,    visualization     tools,    and    report    generation                      transition   makes   ADK   an   ideal   model   system   for   studying
capabilities,    facilitate    the    development    of    a    workflow    for                   protein conformational  changes due to its well-defined  states.
training    and    prediction    of    conformational    properties,    e.g.                      Details of the open-close conformational  transition have been
functional   state  labels,  based  on  learned  graph  embeddings.                               extensively  investigated  through  combinations  of experimen-
The class diagram of MDGraphEmb is presented in Fig. 1.                                           tal     and     computational     methods     (Henzler-Wildman            et          al.
2.2 Graph embedding and machine                                                                   2007,     Daily       et      al.   2010, Ping       et      al.   2013, Formoso       et      al.
learning prediction                                                                               2015, Wang  et al. 2020a). ADK dynamics is compatible  with
                                                                                                  an  induced-fit   model   and  a  complete   transition   to  a  closed
The    workflow    of    the    MDGraphEmb    toolkit    is    shown    in                        state  is generally  observed  in the presence  of the substrate.  A
Fig.    2.   Protein    simulation    data    is   read    using    MDAnalysis                    recent  computational  study  demonstrated  that  a  double  mu-
(Fig.  2a),  where  the  coordinates  of  the  Cα         atoms  in  the  pro-                    tant (V135G,  V142G)  shows features  of pre-existing  equilib-
tein are represented by an ðX;                               Y ;   ZÞ         matrix, and n denotes the rium  and  can  sample   the  closed   state   in  the  absence   of  the
number of frames in the protein trajectory.  For each frame, a                                    substrate  (Song  et  al. 2021). Mutations  at residues  V135 and
pairwise  Cα         distance  matrix  is  calculated,  filtered  by  a  con-                     V142   are   located   on   the   lid   domain   of   ADK,   in   a   flexible
tact cut-off  (default:  values    < 10Å) (Gligorijevi �c  et  al. 2021),                         loop   region   directly   involved   in   the   conformational   transi-
and converted  into a weighted graph, where edge weights are                                      tion.      The      structural      architecture      of      ADK      is      illustrated
calculated as ð1                                        − ðdistance=cut-off                                         Þ).in Fig. 3.

## Page 4

4                                                                                                                                                                                                                  Hossein Nezhad et al.






























Figure 1. Class diagram of the MDGraphEmb toolkit. A detailed explanation can be found in the Section 2.






































Figure 2. Workflow of the MDGraphEmb toolkit. (a) Protein simulation data is read by MDAnalysis,                                                               where ðX      ;   Y  ;   Z Þ   are Cα        atom coordinates and n is the
number of frames in protein trajectory. The protein data is converted into graph using the Cα        distance matrix, with the adjacency matrix constructed
using a default cutoff of 10 Å. Graphs for each frame are then generated using the NetworkX library. (b) The graphs are embedded using PyTorch
Geometric,                                                         with options for various embedding methods. (C) The embedding produces a series of matrices, each of size jV   j   × jd   j,   where jV   j   is the
number of nodes and jd   j   is the embedding dimension. Each frame in the trajectory results in one matrix, which is reshaped into a vector. The trajectory is
represented in a tabular data format where a per-frame target value can be added. (d) This data structure is ready for machine learning classification
tasks. In this paper, a classification of protein functional states is presented.

   In addition to the ADK case study, MDGraphEmb was fur-                                             2.4 System preparation and simulation
ther  evaluated  on  two  structurally  and  dynamically  distinct                                    The  wild-type  structure  of  ADK  was  downloaded  from  the
systems—PlnE  and  HIV-1  protease,  to  assess  the  generaliz-                                      Protein  Data  Bank  (Berman     et     al.  2003).  A  double  mutant
ability   of   the   approach.   PlnE   is   an                 α-helical        antimicrobial        (V135G  þ    V142G)  was  generated  from  this  structure  (PDB
peptide   with   high   conformational   flexibility,   while   HIV-1                                 ID:      4AKE)      using      PyRosetta      (Chaudhury             et             al.      2010).
protease exhibits pronounced flap dynamics that regulate ac-                                          Sampling   of   conformational   changes   in   ADK   was   done   by
cess  to  its  active  site.  These  systems  were  selected  to  test  the                           MD  simulation  using  GROMACS  2022.4  with  the  AMBER
method   across   different   types   of   conformational   dynamics.                                 ff99SB�-ILDN   force   field.    Details    of   system    minimization
Full    details    are    provided    in    the        Supplementary    Materials                     and       equilibration       are       reported       in       the     Supplementary
(Case  Study  Systems:  Preparation  and  Simulation),  available                                     Materials       (Case  Study  Systems:  Preparation  and  Simulation
as supplementary data              at Bioinformatics online.                                          Supplementary   Materials),   available   as                    supplementary   data

## Page 5

MDGraphEmb                                                                                                                                                                                                                                5








































Figure 3. Machine learning target labels for the ADK conformational classification scenario, derived using PCA on MD trajectory data. (a) PC1 (see also x-
axis in panel b) describes open–closed conformational transition in ADK, while PC2 (y-axis)         describes the twisting motion of the LID domain. The
structural architecture of ADK comprises three domains: the CORE domain (green; residues 1–29, 68–117, 161–214), the NMPbind domain (red; residues
30–67), and the LID domain (orange; residues 118–160). While the CORE domain acts as a stable scaffold, the NMPbind and LID domains undergo
conformational changes, closing over ligand binding sites during catalysis. (b) A density contour plot estimates the distribution of conformational states in
this PCA space. Based on density thresholds, four hypothetical states were defined: open (A), closed (B), intermediate (I), and non-state (N).


at    Bioinformatics  online.  For  the  wild-type  and  double  mu-                        a density  analysis  was  performed.  Contour  lines were gener-
tant  structures,  5  replicas  of  1  microsecond  (μs)          were  gener-              ated,  and  the  maximal  contour  threshold  that  separates  the
ated  using  a  2-femtosecond  timestep.  A  dataset  of  100  000                          two basins of open and closed conformations was identified,
frames   recorded   every   10   picoseconds   was   created   for   this                   that  in  the  case  of  (PC1,  PC2)  space  corresponded  to  0.02
study from the  replica R02 of the  double mutant, that  is the                             units of density over the total space area. Finally, boundaries
one   with   the   most   extensive   transition   towards   the   closed                   for  each  area  in  the  (PC1,  PC2)  space  with  a  density  higher
state, so the one more informative for effective training.                                  than   the   threshold   were   defined.   All   data   points   (frames)
2.5 Conformational state prediction                                                         within  each  area  were  labelled  accordingly:  open  (A),  closed
                                                                                            (B),   intermediate    (I).    All    remaining    data   points    in    lower-
The aim of this study is to demonstrate that graph embedding                                density regions were labelled non-state (N).
effectively    captures    information    on    protein    conformations                       While this procedure does not follow a rigorous free energy
from  MD  simulation  data  and  can  be  used  to  train  machine                          reconstruction, it offers a robust framework to test the poten-
learning models to predict conformational states. To this end,                              tial of machine learning in predicting state labels. These labels
we  designed  a  prediction  scenario  where  a  supervised  learn-                         are generated in a non-trivial and non-linear way, avoiding a
ing   model   is   trained   to   classify   conformational   states.   The                 direct  dependency  on  the  coordinates  of  individual  frames.
scenario was tested on the MD trajectory of the ADK transi-                                 Additionally,  the  state  boundaries   do  not  define  any   easily
tion from the open to the closed state.                                                     calculable hyperplane in the PCA space. Information on PCA
   Initially,   a   state   label   was   generated   for   each   trajectory               will not be used in the next steps of model training to add ro-
frame    using    a    non-trivial    procedure    that    included    expert               bustness   to   the   test.   With   a   suitable   target   variable   estab-
knowledge   decisions:   states   associated   with   energy   minima                       lished,    a    model    can    be    trained    to    learn    the    relationship
were identified as high-density regions in the conformational                               between the input conformation, as represented by the graph
space    describing     ADK     dynamics.     First,    critical     collective             embedding, and the output target label representing the con-
motions    describing    ADK    dynamics    were    extracted    using                      formational state of that conformation (see Fig. 2c).
Principal Component Analysis  (PCA) calculated over a com-                                     A  set  of  supervised  machine  learning  algorithms  was  used
bined trajectory of wild-type and double mutant simulations                                 to train and test a classification model using different subsets
(Amadei   et   al.  1993).  The  first  principal  component  (PC1—                         of frames from the protein trajectory (5000, 10 000, 25 000,
39.5%  explained  variance)  clearly  describes  the  lid  closure,                         50  000,  and  100  000).  Subsets  were  derived  by  striding  at
while   the   second   principal   component   (PC2—24.0%)   cap-                           200,  100,  40,  20,  and  10  ps.  All  subsets  contained  frames
tures  the  twisting  motion  of  the  lid,  known  to  lock  the  con-                     representative  of  the  three  main  conformational  states.  The
formation in the closed state (Fig. 3a). Second, the dataset of                             models were trained on 70% of the data. Following training,
conformations was projected onto the (PC1, PC2) space, and                                  the models were evaluated on the remaining 30% of the data

## Page 6

6                                                                                                                                                                                                                  Hossein Nezhad et al.

to  assess  their  predictive  performance.  This  evaluation  was                      machine     learning     models     using     GraphSAGE     embeddings
conducted using different combinations of embedding techni-                             across  different  frame  counts.  The  extended  analysis  covers
ques, machine learning models, and different dataset sizes to                           not   only   the   ADK   system,   but   also   two   additional   protein
identify the best predictive framework.                                                 systems:  PlnE  and  HIV-1  protease.  Embeddings  were  gener-
2.6 Statistical analysis and visualization tools                                        ated  with  GAT,  GCN,  GraphSage,  and  Node2Vec.  Among
                                                                                        these, GraphSage demonstrated superior performance, gener-
Initial  data  cleaning,  preparation,  statistical  analysis,  and  fi-                ating      high-quality      embeddings      that      consistently      outper-
nal  plots  were  generated  using  the  R  statistical  environment                    formed      the      other      methods.      GraphSage      was      ultimately
(R   Core   Team   2021).   Density   analysis   and   state   labelling                selected as the optimal method due to its scalability and abil-
were performed using the MASS (Venables and Ripley 2002)                                ity    to    handle    high-dimensional    data    efficiently.    Machine
and  sp  (Pebesma  and  Bivand  2005)  libraries.  Images  of  pro-                     learning  models  trained  on  GraphSage  embeddings  achieved
tein    structures    were    generated    using    PyMol    (Schr €odinger,            the highest overall performance, highlighting its robustness in
LLC 2015) and VMD (Humphrey et al. 1996).                                               capturing the underlying structure of the data.
                                                                                           The following presents a comparative performance analysis
3 Results and discussion                                                                of  different  machine  learning  models  trained  on  embeddings
                                                                                        generated  by  the  GraphSage  method.  The  evaluated  models
Different predictive models were trained and tested to classify                         include Logistic Regression (LR), Random Forest (RF), XGB,
conformational states at the frame level for the ADK system.                            LGBM,   NN,   CNN,   and   Support   Vector   Machines   (SVM).
Three key aspects of the data analysis workflow were investi-                           Each model was assessed based on its overall performance in
gated:  (i)  the  choice  of  embedding  methods,  (ii)  the  machine                   classification,  as  well  as  correct  predictions  across  the  single
learning  models,  and  (iii)  the  dataset  sizes  (see Table  1).  For                class labels: Class A (open state), Class B (closed state), Class
details refer to the Supplementary Materials               (Results section),           I  (intermediate  state),  and  Class  N  (non-state).  The  evalua-
available   as    supplementary   data         at       Bioinformatics   online.        tion    was    conducted    across    different    dataset    sizes    (5000,
This includes a comparison of class-specific and overall accu-                          10   000,   25   000,   50   000,   and   100   000   frames),   providing
racy across different embedding methods, as well as an evalu-                           insights   into   model   performance   with   increasing   data   size
ation   of   various   performance   metrics   by   class   for   multiple              and frequency of sampling from the original MD trajectory.



Table 1. Comparison of class-specific and overall accuracy across different frames and machine learning models for GraphSage.

Trajectory size               ML Model                           Class A               Class B               Class I              Class N               Model Accuracy

5000                          Logistic Regression                  0.57                  0.95                 0.43                  0.74                       0.74
                              Random Forest                        0.28                  0.97                 0.43                  0.88                       0.81
                              XGBoost                              0.27                  0.97                 0.55                  0.90                       0.83
                              LightGBM                             0.24                  0.97                 0.55                  0.92                       0.83
                              Neural Network                       0.47                  0.98                 0.48                  0.81                       0.78
                              CNN                                  0.30                  0.96                 0.39                  0.88                       0.81
                              Support Vector                       0.31                  0.97                 0.30                  0.89                       0.82
10 000                        Logistic Regression                  0.62                  0.95                 0.63                  0.73                       0.75
                              Random Forest                        0.39                  0.98                 0.54                  0.88                       0.82
                              XGBoost                              0.28                  0.98                 0.58                  0.91                       0.82
                              LightGBM                             0.28                  0.98                 0.53                  0.90                       0.82
                              Neural Network                       0.47                  0.97                 0.70                  0.85                       0.81
                              CNN                                  0.41                  0.97                 0.47                  0.85                       0.80
                              Support Vector                       0.34                  0.98                 0.41                  0.91                       0.83
25 000                        Logistic Regression                  0.72                  0.96                 0.86                  0.69                       0.74
                              Random Forest                        0.35                  0.98                 0.63                  0.86                       0.80
                              XGBoost                              0.28                  0.97                 0.69                  0.91                       0.83
                              LightGBM                             0.32                  0.97                 0.69                  0.89                       0.82
                              Neural Network                       0.58                  0.98                 0.77                  0.82                       0.81
                              CNN                                  0.31                  0.94                 0.53                  0.90                       0.82
                              Support Vector                       0.40                  0.97                 0.63                  0.89                       0.83
50 000                        Logistic Regression                  0.78                  0.98                 0.92                  0.67                       0.73
                              Random Forest                        0.45                  0.98                 0.72                  0.86                       0.82
                              XGBoost                              0.34                  0.98                 0.78                  0.90                       0.84
                              LightGBM                             0.38                  0.98                 0.79                  0.89                       0.83
                              Neural Network                       0.52                  0.97                 0.72                  0.91                       0.86
                              CNN                                  0.45                  0.96                 0.73                  0.87                       0.82
                              Support Vector                       0.50                  0.98                 0.76                  0.89                       0.84
100 000                       Logistic Regression                  0.81                  0.98                 0.95                  0.67                       0.74
                              Random Forest                        0.47                  0.98                 0.72                  0.86                       0.82
                              XGBoost                              0.40                  0.96                 0.68                  0.91                       0.84
                              LightGBM                             0.40                  0.97                 0.75                  0.90                       0.84
                              Neural Network                       0.68                  0.97                 0.71                  0.87                       0.85
                              CNN                                  0.51                  0.96                 0.67                  0.88                       0.83
                              Support Vector                       0.59                  0.97                 0.77                  0.88                       0.85

Highest values by Class for each trajectory size are indicated in bold.

## Page 7

MDGraphEmb                                                                                                                                                                                                                                7

   In terms of overall accuracy, NN achieved the highest accu-                              when   more   data   is   available,   as   LR   can   detect   overarch-
racy  for  a  dataset  of  50  000  frames,  with  a  performance  of                       ing trends.
0.86,     indicating     their     robustness     across     all     classes.     LR,          Similar  to  Class  B,  Class  N  was  predicted  with  high  accu-
LGBM,  and  XGB  also  showed  strong  overall  performance,                                racy  across  most  models.  LGBM  demonstrated  the  best  per-
especially  at  smaller  and  intermediate  dataset  sizes,  making                         formance at smaller trajectory sizes, achieving an accuracy of
them      suitable      choices      when      prioritizing      computational              0.92   for   5000   frames.   For   larger   trajectory   sizes   (50   000
efficiency.                                                                                 frames),    Neural    Networks    achieved    an    accuracy    of    0.91,
   The open state (Class A) presented considerable challenges                               showcasing their adaptability with increased data and capac-
for most machine learning models to predict accurately, while                               ity  to  capture  complex,  distributed  patterns.  A  projection  of
LR    performed    exceptionally    well    at    larger    dataset    sizes,               the correctness of predictions on the (PC1, PC2) space for LR
achieving an accuracy of 0.78 for 50 000 frames and 0.81 for                                and   NN   is   reported   in      Figs   4   and    5,   respectively,   on   the
100  000  frames.  The  closed  state  (Class  B)  was  the  easiest                        100  000-frame  dataset  with  GraphSage  embeddings,  where
class to predict, with consistently high accuracy across mod-                               ADK   states   are   colour-coded:   blue   dots   for   the   open   state
els and trajectory sizes. Most models achieved top accuracies                               (A),  pink  for  the  intermediate  state  (I),  orange  for  the  close
above  0.95  across  different  trajectory  sizes,  showcasing  the                         state (B), and grey for the non-state (N), while incorrect pre-
well-defined and easily recognizable patterns within Class B.                               dictions are shown as red dots.
This aligns with what is expected: the closed state of the pro-                                An  overview  of  the  performance  across  dataset  sizes  (see
tein   has   a   distinct,   defined   set   of   conformations   mapping                   Table  1)  suggests  that  50  000  frames  is  the  optimal  size,  of-
onto   a   well-separated   region   of   the   phase   space,   while   the                fering   the   highest   balanced   accuracy   across   protein   states.
open state can appear in different geometrical arrangements,                                This dataset size is consistent with the sampling of conforma-
making it more challenging to identify a common pattern.                                    tions every  20  ps.  This timescale  aligns with  loop  rearrange-
   Class  I  was  the  most  challenging  to  predict  for  all  models                     ments      and      small      domain      motions      underpinning      larger
compared to Classes A and B. Neural Networks achieved the                                   conformational  changes.  This  dataset  size  represents  a  good
highest accuracy of 0.70 at the trajectory size of 10 000, dem-                             compromise for training on trajectories of up to the μs      scale.
onstrating  their  ability  to  capture  the  non-linear  characteris-
tics of the intermediate state. The transitional nature of Class                            4 Conclusion
I makes it difficult  to define, as it represents an  intermediate
phase between the open and closed states of the protein. For                                In  this  study,  we  introduced  MDGraphEmb,  the  first  open-
larger trajectory sizes (50 000 and 100 000 frames), Logistic                               source,  domain-specific  toolkit  for  encoding  protein  confor-
Regression showed improved performance with accuracies of                                   mational dynamics  from protein  MD  simulations  into graph
0.92 and 0.95, respectively. This pattern suggests that, while                              embeddings   suitable   for   machine   learning.   Unlike   general-
Class I may display complex transitional properties at smaller                              purpose  frameworks  such  as  PyG  and  DGL,  MDGraphEmb
dataset   sizes,   it   benefits   from   linear   classification   methods                 provides     a     complete     and     tailored     workflow,     from     MD






































Figure 4. The PCA plot shows the Logistic Regression’s state predictions for 100 000 frames, using color coding to distinguish between ADK states. Red
dots indicate incorrect predictions, while blue, pink, and grey dots represent correct predictions for the open (A), intermediate (I), and non-state (N),
respectively.

## Page 8

8                                                                                                                                                                                                                  Hossein Nezhad et al.






































Figure 5. The PCA plot shows the neural network’s state predictions for 100 000 frames, using color coding to distinguish between ADK states. Red
dots indicate incorrect predictions, while blue, pink, and grey dots represent correct predictions for the open (A), intermediate (I), and non-state (N),
respectively.

trajectory   preprocessing   to   graph   construction,   embedding                             The    MDGraphEmb    library    can    be    readily    extended    to
generation,  and  classification.  It  integrates  multiple  embed-                         study and characterize long MD simulations. Additionally, it
ding   methods   (Node2Vec,   GCN,    GAT,   and   GraphSAGE)                               may  serve  as  a  valuable  tool  for  investigating  the  impact  of
and various machine learning models.                                                        mutations on the intrinsic dynamics of proteins by comparing
   We    addressed    the    core    challenge    of    compressing    high-                different   state   samples.   Overall,   MDGraphEmb   lowers   the
dimensional structural dynamics into informative representa-                                barrier  to  applying  graph  learning  in  molecular  simulations
tions    by    encoding    and    compressing    information    in    graph                 and enables scalable, reproducible, and biologically meaning-
models   to   enhance   the   signal-to-noise   ratio   and   transform                     ful analysis of protein dynamics. It offers a practical founda-
molecular dynamics data into a tabular format suitable for ef-                              tion for applications such as mutation impact analysis, long-
fective  machine  learning  predictions.  By  systematically  com-                          timescale trajectory annotation, and automated state classifi-
paring   graph   embedding   methods,   we   evaluated   how   well                         cation in high-throughput workflows.
each approach preserved signal relevant to protein state clas-
sification.  Among  them,  GraphSAGE  offered  the  best  trade-
off   between   expressiveness   and   scalability,   particularly   for                    Acknowledgements
large   datasets.   We   showed   how   supervised   models   can   be                      The     authors     would     like     to     thank     the     members     of     the
trained  to  predict  frame-level  properties  on  unseen  data. We                         Computational Biology research group for their critical feed-
demonstrated this by classifying the conformational states of                               back and valuable suggestions on the project.
the   ADK   protein,   which   exhibits   distinct   functional   transi-
tions, including intermediate and transient states between ex-
perimentally   characterized   open   and   closed   conformations.                         Author contributions
To         evaluate         the         generalizability         of         the         approach, Ferdoos    Hossein    Nezhad    (Conceptualization    [lead],    Data
MDGraphEmb  was  also  tested  on  two  structurally  and  dy-                              curation  [lead],  Formal  analysis  [lead],  Investigation  [lead],
namically   diverse   systems:   PlnE,   an                α-helical        antimicrobial   Methodology [lead], Project administration [equal], Software
peptide with a high degree of conformational flexibility, and                               [lead],   Supervision   [equal],   Validation   [lead],   Visualization
HIV-1   protease,   which   undergoes   large-scale   loop   opening                        [equal],  Writing—original  draft  [equal],  Writing—review  &
and   closing   motions   that   regulate   access   to   its   active   site.              editing  [equal]),  Namir  Oues  (Data curation  [equal],  Formal
These contrasting systems demonstrate that MDGraphEmb is                                    analysis        [equal],        Writing—review        &        editing        [equal]),
suitable  for  proteins  with  a  spectrum  of  dynamics  changes,                          Massimiliano   Meli   (Formal   analysis   [equal],   Methodology
different structural classes and functional mechanisms.
   While clustering remains a useful exploratory tool, it strug-                            [equal],  Writing—review  &  editing  [equal]),  and  Alessandro
gles  to  capture  continuous  transitions  and  generalize  across                         Pandini   (Conceptualization   [equal],   Data   curation   [equal],
simulations. The supervised learning approach presented here                                Formal         analysis         [equal],         Funding         acquisition         [lead],
addresses  these  limitations  by  learning  from  labelled  exam-                          Investigation  [equal],  Methodology  [equal],  Project  adminis-
ples,   enabling   robust   and   scalable   prediction   of   conforma-                    tration          [equal],          Resources          [lead],          Software         [equal],
tional states in new datasets.                                                              Supervision [equal], Validation [equal], Visualization [equal],

## Page 9

MDGraphEmb                                                                                                                                                                                                                                9

Writing—original    draft    [equal],     Writing—review     &    edit-                                Gowers RJ, Linke M, Barnoud J  et  al.  Mdanalysis:  A  Python  Package
ing [equal])                                                                                                for     the     Rapid     Analysis     of     Molecular     Dynamics     Simulations.                                           Los
                                                                                                            Alamos,   NM   (United   States):   Los   Alamos   National   Laboratory
                                                                                                            (LANL), 2019. https://doi.org/10.25080/Majora-629e541a-00e
Supplementary data                                                                                     Grover A, Leskovec J. node2vec: Scalable feature learning for networks. In:
Supplementary data              are available at Bioinformatics online.                                     Proceedings   of   the   22nd   ACM   SIGKDD   International   Conference   on
                                                                                                            Knowledge Discovery and Data Mining.                         2016, 855–64.
Conflict of interest: None declared.                                                                   Hagberg A, Swart PJ, Schult DA. Exploring network structure, dynam-
                                                                                                            ics,   and   function   using   networkx.   In:   Varoquaux   G,   Vaught   T,
                                                                                                            Millman    J    (eds.),          Proceedings          of          the          7th          Python          in          Science
Funding                                                                                                     Conferences (SciPy2008),                                                                                                           Pasadena, CA USA.                2008, 11–5.
N.O. was supported by a scholarship from Brunel University                                             Hagg  A,  Kirschner  KN.  Open-source  machine  learning  in  computa-
                                                                                                            tional  chemistry.  J  Chem  Inf  Model  2023;63:4505–32.                    https://doi.
London   EPSRC   DTP    [EP/T518116/1].                                                                        This   project   made org/10.1021/acs.jcim.3c00643
use of time on HPC granted via the UK High-End Computing                                               Hamilton WL, Ying Z, Leskovec J. Inductive representation learning on
Consortium  for  Biomolecular  Simulation,  HECBioSim,  sup-                                                large graphs. Adv Neural Inf Process Syst 2017;30:1024–34.
ported  by  EPSRC  [EP/X035603/1].                                                                        Collaborative  work  be-Henzler-Wildman    K,    Kern    D.    Dynamic    personalities    of    proteins.
tween    F.HN.,    M.M.,    and    A.P.    was    supported    by    Royal                                  Nature 2007;450:964–72.
Society International Exchanges 2024 Cost Share (Italy only)                                           Henzler-Wildman KA, Lei M, Thai V et al. A hierarchy of timescales in
[IEC\R2\242053].                                                                                 This       work       was       supported       by       the protein    dynamics    is    linked    to    enzyme    catalysis.        Nature    2007;
                                                                                                            450:913–6.
CINECA       award       under       the       ISCRA       initiative       (project                   Humphrey W, Dalke A, Schulten K. Vmd – visual molecular dynamics.
HP10BKFH8P),  which  provided  access  to  high-performance                                                 J Mol Graph 1996;14:33–8.
computing resources and technical support.                                                             Jin  W,  Barzilay  R,  Jaakkola  T.  Junction  tree  variational  autoencoder
                                                                                                            for   molecular   graph   generation.     Int     Conf     Machine     Learn   2018;
                                                                                                            80:2323–32.
Data availability                                                                                      Jin  Y,  Johannissen  LO,  Hay  S.  Predicting  new  protein  conformations
Relevant  data  underpinning  this  publication  can  be  accessed                                          from   molecular   dynamics   simulation   conformational   landscapes
from  Brunel  University  London’s  data  repository  under  CC                                             and machine learning. Proteins 2021;89:915–21.                     https://doi.org/10.
                                                                                                            1002/prot.26068
BY licence: https://doi.org/10.17633/rd.brunel.c.7664645.                                              Kaptan S, Vattulainen I. Machine learning in the analysis of biomolecu-
                                                                                                            lar simulations. Adv Phys X 2022;7:2006080.
                                                                                                       Kipf TN, Welling M. Semi-supervised classification with graph convo-
References                                                                                                  lutional  networks.  In:     5th     International     Conference     on     Learning
Abadi M, Agarwal A, Barham P et al. Tensorflow: large-scale machine                                         Representations.                                                       2017.
    learning          on          heterogeneous          distributed          systems.          arXiv, Lemke T, Peter C. Encodermap: dimensionality reduction and genera-
    arXiv:1603.04467,               https://doi.org/10.48550/arXiv.1603.04467,                              tion   of   molecule   conformations.     J     Chem     Theory     Comput   2019;
    2016, preprint: not peer reviewed.                                                                      15:1209–15.
Amadei A, Linssen AB, Berendsen HJC. Essential dynamics of proteins.                                   Lemke T, Berg A, Jain A  et  al. Encodermap (ii): visualizing important
    Proteins 1993;17:412–25.             https://doi.org/10.1002/prot.340170408                             molecular motions with improved generation of protein conforma-
Berman H, Henrick K, Nakamura H. Announcing the worldwide pro-                                              tions. J Chem Inf Model 2019;59:4550–60.
    tein data bank. Nat Struct Biol 2003;10:980.                                                       Lin B, Luo X, Liu Y et  al. A comprehensive review and comparison of
Boadu F, Lee A, Cheng J. Deep learning methods for protein function                                         existing   computational   methods   for   protein   function   prediction.
    prediction. Proteomics 2025;25:e2300471.                                                                Brief Bioinf 2024;25:bbae289.
Chaudhury S, Lyskov S, Gray JJ. Pyrosetta: a script-based interface for                                Michaud-Agrawal N, Denning EJ, Woolf TB et al. MDAnalysis: a tool-
    implementing      molecular      modeling      algorithms      using      rosetta.                      kit  for  the  analysis  of  molecular  dynamics  simulations.   J   Comput
    Bioinformatics    2010;26:689–91.                https://doi.org/10.1093/bioinfor                       Chem 2011;32:2319–27.
    matics/btq007                                                                                      Nelson W, Zitnik M, Wang B et al. To embed or not: network embed-
Cui  P,  Wang  X,  Pei  J    et    al.  A  survey  on  network  embedding.    IEEE                          ding  as  a  paradigm  in  computational  biology.   Front   Genet  2019;
    Trans Knowl Data Eng 2019;31:833–52.                                                                    10:381.
Daily MD, Phillips GNJ, Cui Q. Many local motions cooperate to pro-                                    Oues  N,  Dantu  SC,  Patel  RJ   et   al.  MDSubSampler:  a  posteriori  sam-
    duce   the   adenylate   kinase   conformational   transition.     J     Mol     Biol                   pling of important protein conformations from biomolecular simu-
    2010;400:618–31.                                                                                        lations. Bioinformatics 2023;39:btad427.
Fey  M,  Lenssen  JE.  Fast  graph  representation  learning  with  pytorch                            Patel AC, Sinha S, Palermo G. Graph theory approaches for molecular
                                                                                                            dynamics simulations. Q Rev Biophys 2024;57:e15.                       https://doi.org/
    geometric.      arXiv,      arXiv:1903.02428,             https://doi.org/10.48550/                     10.1017/S0033583524000143
    arXiv.1903.02428,          2019, preprint: not peer reviewed.                                      Pebesma  EJ,  Bivand  R.  Classes  and  methods  for  spatial  data  in  R.   R
Formoso E, Limongelli V, Parrinello M. Energetics and structural char-                                      News 2005;5:9–13.
    acterization of the large-scale functional motion of adenylate kinase.                             Pedregosa  F,  Varoquaux  G,  Gramfort  A    et    al.  Scikit-learn:  machine
    Sci Rep 2015;5:8425.                                                                                    learning in Python. J Mach Learn Res 2011;12:2825–30.
Glielmo A, Husic BE, Rodriguez A et al. Unsupervised learning methods                                  Ping J, Hao P, Li Y-X et al. Molecular dynamics studies on the confor-
    for    molecular    simulation    data.         Chem         Rev    2021;121:9722–58.                   mational transitions of adenylate kinase: a computational evidence
    https://doi.org/10.1021/acs.chemrev.0c01195                                                             for the conformational selection mechanism. Biomed Res Int 2013;
Gligorijevi�c V, Renfrew PD, Kosciolek T et al. Structure-based protein                                     2013:628536.
    function     prediction     using     graph     convolutional     networks.          Nat           R    Core    Team.          R:          A          Language          and          Environment          for          Statistical
    Commun          2021;12:3168.             https://doi.org/10.1038/s41467-021-                           Computing.                                              Vienna,       Austria:       R       Foundation       for       Statistical
    23303-9                                                                                                 Computing, 2021.

## Page 10

10                                                                                                                                                                                                                Hossein Nezhad et al.


Schr €odinger  LLC.    The    PyMOL    Molecular    Graphics    System,    Version                           Yi H-C, You Z-H, Huang D-S  et  al. Graph representation learning in
    3.0.0.                  2015. https://www.pymol.org/support.html                                              bioinformatics:    trends,    methods    and    applications.         Brief         Bioinf
Song H, Wutthinitikornkit Y, Zhou X et al. Impacts of mutations on dy-                                            2022;23:bbab340.
    namic allostery of adenylate kinase. J Chem Phys 2021;155:035101.                                        You  J,  Liu  B,  Ying  Z    et    al.  Graph  convolutional  policy  network  for
Veli�ckovi            �c  P,  Ying  R,  Padovano  M    et    al.  Neural  execution  of  graph  algo-             goal-directed  molecular  graph  generation.   Adv   Neural   Inf   Process
    rithms. In: International Conference on Learning Representations.                                                     2020.Syst 2018;31:6412–22.
Venables  WN,  Ripley  BD.  Modern  Applied  Statistics  with  S,      4th  edn.                             You  J,  Ying  Z,  Leskovec  J.  Design  space  for  graph  neural  networks.
    New York: Springer, 2002.                                                                                     Adv Neural Inf Process Syst 2020.
Wang J, Peng C, Yu Y  et  al. Exploring conformational change of ade-                                        Yue X, Wang Z, Huang J  et  al. Graph embedding on biomedical net-
    nylate  kinase  by  replica  exchange  molecular  dynamic  simulation.                                        works:     methods,     applications     and     evaluations.           Bioinformatics
    Biophys J 2020a;118:1009–18.                                                                                  2020;36:1241–51.           https://doi.org/10.1093/bioinformatics/btz718
Wang  M,  Zheng  D,  Ye  Z   et   al.  Deep  graph  library:  a  graph-centric,                              Zhang W, Chen Y, Li D et al. Manifold regularized matrix factorization
    highly-performant    package    for    graph    neural    networks.    arXiv,                                 for   drug-drug   interaction   prediction.     J     Biomed     Inform   2018;88:
    arXiv:1909.01315, 2020b, preprint: not peer reviewed.                                                         90–7. https://doi.org/10.1016/j.jbi.2018.11.005
Wu Y, Chen Y, Yin Z  et  al. A survey on graph embedding techniques                                          Zitnik M, Leskovec J. Predicting multicellular function through multi-
    for biomedical data: methods and applications. Information Fusion                                             layer  tissue  networks.    Bioinformatics  2017;33:i190–8.                      https://doi.
    2023;100:101909.            https://doi.org/10.1016/j.inffus.2023.101909.                                     org/10.1093/bioinformatics/btx252

























































© The Author(s) 2025. Published by Oxford University Press.
This is an Open Access article distributed under the terms of the Creative Commons Attribution License (https://creativecommons.org/licenses/by/4.0/),                                                                                                                                        which permits
unrestricted reuse, distribution, and reproduction in any medium, provided the original work is properly cited.
Bioinformatics, 2025, 41, 1–10
https://doi.org/10.1093/bioinformatics/btaf420
Original Paper
