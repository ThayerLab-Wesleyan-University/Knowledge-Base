## Page 1

Wesleyan University                                                               The Honors College 
 
 
 
 
 
 
 
 
 
 
 
 
Guidance in Diffusion Models for Target-Aware 
Molecular Generation 
 
by 
 
Jeremy Theodore Zay 
Class of 2026 
 
 
 
 
 
 
 
A thesis submitted to the 
faculty of Wesleyan University 
in partial fulfillment of the requirements for the 
Degree of Bachelor of Arts 
with Departmental Honors in Computer Science and College of 
Integrative Sciences 
 
Middletown, Connecticut    April, 2026

## Page 2

Guidance in Diffusion Models for Target-Aware

                          Molecular Generation



Abstract




Thisthesisinvestigateswhetherthesamplingofatarget-awaremoleculardiffusion

model can be improved by applying guidance from an external scoring function.

UsingTargetDiff[1]onmutantp53Y220C[2],wetrainasurrogateaffinitymodel

fromdockedgeneratedmolecules[3]andtestwhetheritcanguidereversediffusion

towardsampleswithhigherbindingaffinity.


Although the surrogate is able to predict affinity well on clean molecules, the im-

provement it has on generation is limited. To better understand this behavoir, we

introducePolyGen2D,acontrolledsynthetictestbedforstudyingguidanceinasim-

plercoordinate-baseddiffusionsetting. Theresultssuggestthatguidanceisuseful

whentheguidancemodeliscompatiblewiththenoisyintermediatestatesencoun-

teredduringreversediffusion.















                                           ii

## Page 3

Acknowledgements



ThereareafewimportantpeopleI’dliketoacknowledge.


Firstly,I’dliketothankmyPI,ProfessorKellyM.Thayer,foryourendlessguidance

(nopunintended)andsupportduringtheprocessofmakingthis.


ThankyouverymuchtoProfessorManfrediandProfessorKrizancforagreeingto

readthis.


Thank you to Mom and Dad for attempting to mitigate my procrastination efforts

(it’shopeless),andforalwayssupportingmeandbelievinginme.


ThankyoutoGrandpa,foralwaysunderstanding.


ThankyoutoYehor,forhavingasmuchfascinationinmachinelearningasIdo.


ThankyoutoAmbrose, forenjoyingsomanylabmeetingstogetherwithme. I’m

gratefultohavefoundtheperfectfriend.


Andthankstoyou,thereader,forenduringthroughthisthesis!
















                                          iii

## Page 4

“What I cannot create, I do not understand.”

                           —RichardFeynman


   iv

## Page 5

Contents




List of Figures                                                                                   ix



List of Tables                                                                                     x



1    Introduction                                                                                  1



2    Background                                                                                    3


    2.1  Notation      . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .             3


    2.2  DrugDiscoveryContext               . . . . . . . . . . . . . . . . . . . . . . .          4


    2.3  p53andtheY220CMutation                 . . . . . . . . . . . . . . . . . . . . .          5


    2.4  MolecularDocking            . . . . . . . . . . . . . . . . . . . . . . . . . .           6


    2.5  MolecularRepresentation            . . . . . . . . . . . . . . . . . . . . . . .          6


    2.6  DeepNeuralNetworks              . . . . . . . . . . . . . . . . . . . . . . . .           7


    2.7  GraphNeuralNetworks             . . . . . . . . . . . . . . . . . . . . . . . .           9


    2.8  SE(3)-Equivariance          . . . . . . . . . . . . . . . . . . . . . . . . . .         10


    2.9  Pre-DiffusionApproaches              . . . . . . . . . . . . . . . . . . . . . .        12


    2.10 DiffusionModels          . . . . . . . . . . . . . . . . . . . . . . . . . . .          13



                                                 v

## Page 6

2.11 DenoisingDiffusionProbabilisticModels                  . . . . . . . . . . . . . .      13


    2.12 GuidanceinDiffusionModels                 . . . . . . . . . . . . . . . . . . . .       15



3    Methods                                                                                     17


    3.1  Overview        . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .           17


    3.2  TargetDiffPipeline          . . . . . . . . . . . . . . . . . . . . . . . . . .         18


           3.2.1  ModelSetup           . . . . . . . . . . . . . . . . . . . . . . . . .         18


           3.2.2  CandidateGenerationandEvaluation                   . . . . . . . . . . . .     19


    3.3  SurrogateGuidance(Molecular)                . . . . . . . . . . . . . . . . . . .       19


           3.3.1  DatasetConstruction           . . . . . . . . . . . . . . . . . . . . .        19


           3.3.2  SurrogateModel            . . . . . . . . . . . . . . . . . . . . . . .        20


           3.3.3  GuidanceMechanism             . . . . . . . . . . . . . . . . . . . . .        20


    3.4  PolyGen2DTestbed            . . . . . . . . . . . . . . . . . . . . . . . . . .         22


           3.4.1  Motivation         . . . . . . . . . . . . . . . . . . . . . . . . . .         22


           3.4.2  DataandRepresentation              . . . . . . . . . . . . . . . . . . .       23


           3.4.3  DiffusionModels           . . . . . . . . . . . . . . . . . . . . . . .        23


           3.4.4  GuidanceObjectives            . . . . . . . . . . . . . . . . . . . . .        24


           3.4.5  SurrogateVariants           . . . . . . . . . . . . . . . . . . . . . .        25


                                                 vi

## Page 7

3.5  ExperimentalDesign            . . . . . . . . . . . . . . . . . . . . . . . . .         26


           3.5.1  TargetDiffExperiments           . . . . . . . . . . . . . . . . . . . .        26


           3.5.2  PolyGen2DExperiments               . . . . . . . . . . . . . . . . . . .       26


           3.5.3  EvaluationMetrics           . . . . . . . . . . . . . . . . . . . . . .        27



4    Results                                                                                     28


    4.1  BaselineTargetDiff          . . . . . . . . . . . . . . . . . . . . . . . . . .         28


    4.2  SurrogatePredictivePerformance                . . . . . . . . . . . . . . . . . .       30


    4.3  GuidedPolyGen2DPerformance                  . . . . . . . . . . . . . . . . . . .       31


    4.4  PolyGen2DBaselineBehavior                . . . . . . . . . . . . . . . . . . . .        32


    4.5  GuidanceinPolyGen2D               . . . . . . . . . . . . . . . . . . . . . . .         33


    4.6  SurrogateVariants        . . . . . . . . . . . . . . . . . . . . . . . . . . .          33


    4.7  ArchitecturalResults          . . . . . . . . . . . . . . . . . . . . . . . . .         34



5    Discussion                                                                                  36


    5.1  CoreFinding          . . . . . . . . . . . . . . . . . . . . . . . . . . . . .          36


    5.2  WhyMolecularGainsRemainLimited                    . . . . . . . . . . . . . . . .       36


    5.3  WhatPolyGen2DClarifies               . . . . . . . . . . . . . . . . . . . . . .        38




                                                vii

## Page 8

5.4  ArchitecturalConsiderations          . . . . . . . . . . . . . . . . . . . . .     38


    5.5  ImplicationsforMolecularGuidance             . . . . . . . . . . . . . . . . .     39



6    Conclusion                                                                             41


    6.1  WhatThisThesisEstablishes            . . . . . . . . . . . . . . . . . . . . .     41


    6.2  WhatRemainsOpen             . . . . . . . . . . . . . . . . . . . . . . . . .      41



Appendix A: Mathematical Details                                                            42



Appendix B: PolyGen2D Output                                                                56



Appendix C: PolyGen2D Output                                                                59



Appendix C: Scripts                                                                         62



References                                                                                  71



















                                             viii

## Page 9

List of Figures


    2.1  Moleculerepresentedasagraph.             . . . . . . . . . . . . . . . . . . .       7

    3.1  TargetDiffDiffusionProcess[1]            . . . . . . . . . . . . . . . . . . .      18

    3.2  PolyGen2D-to-TargetDiffresearchworkflow.                . . . . . . . . . . . .     22

    3.3  OneguidedreversestepinPolyGen2D                 . . . . . . . . . . . . . . . .     24

    3.4  PolyGen2Dmethodology             . . . . . . . . . . . . . . . . . . . . . . .      27

    4.1  DockedgeneratedmoleculeonY220C                  . . . . . . . . . . . . . . . .     28

    4.2  Scoredistributionofgeneratedmolecules               . . . . . . . . . . . . . .     29

    4.3  Topgeneratedcandidates           . . . . . . . . . . . . . . . . . . . . . . .      29

    4.4  Surrogateaffinitymodelstandaloneperformance.                 . . . . . . . . . .    30

    4.5  PolyGen2Dunguidedfixed-sizeresultsacrossarchitectures.                    . . . .   32

    4.6  PolyGen2Dunguidedvs. guided(fixed-sizedMLP)                    . . . . . . . . .    33

    4.7  PolyGen2DGuidedSamplingPerformance                    . . . . . . . . . . . . .     34

    5.1  Overlayofguidedandunguidedgeneratedmolecules.                    . . . . . . . .    37

    6.1  Trajectoryofdenoisingapolygon.             . . . . . . . . . . . . . . . . . .      56

    6.2  PolyGen2Dtrainingdata.           . . . . . . . . . . . . . . . . . . . . . . .      57

    6.3  PolyGen2Dgenerateddata.            . . . . . . . . . . . . . . . . . . . . . .      58

    6.4  MoleculesgeneratedbyTargetDiff.               . . . . . . . . . . . . . . . . .     59

    6.5  MoremoleculesgeneratedbyTargetDiff.                 . . . . . . . . . . . . . .     60

    6.6  Moreoverlayedguidedandunguidedmolecules.                     . . . . . . . . . .    61






                                              ix

## Page 10

List of Tables


    2.1  Mainnotationused.          . . . . . . . . . . . . . . . . . . . . . . . . . .         3

    4.1  Guidedminusbaseline.           . . . . . . . . . . . . . . . . . . . . . . . .        31















































                                                x

## Page 11

1   Introduction



Eventually, the entire universe will be pure noise, as the last stars and black holes

dissolve and the average temperature of the universe drifts towards absolute zero.

Physics tells us that entropy can never decrease over time in an isolated system,

so how is it possible that a machine learning model can learn to reverse chaos by

removing the noise from a digital object? It seems paradoxical – the idea that an

imagemadeentirelyofTVstaticcanbemanipulatedintoanindistinguishablepho-

tograph,orthatavectorinitializedfromanormaldistributioncanbeformedintoa

moleculethatrestoresamutantproteinandcuresatypeofcancer.


PopularizedbyDALL-EandStableDiffusioninimagegeneration,currentstate-of-

the-artdiffusionmodelscangeneraterealisticdatawithastoundingaccuracy,tothe

pointwhereageneratedimageofafacecanfoolahumanbrainwhichhasevolved

overhundredsofthousandsofyearstorecognizeitsmostminutedetails.


Anaturaldomainfortheuseofthistechnologyisdrugdiscovery,andthismethod

hasbeenadaptedtoenablegenerationofmoleculesthatbindtoaspecificprotein.

Thenextphaseofdrugdiscovery–identifyingamoleculethatnotonlybindstobut

alsorestoresthefunctionofamutantprotein–isstillanopenfrontierofresearch.

Aswepursueacomputationallyefficientwaytoscoreamoleculeontherestorative

effect it will have on a protein, we must have a framework prepared for a scoring

functiontobeintegratedintothemoleculargenerationprocessoncesuchafunction



                                             1

## Page 12

inevitablyexists. Inthisthesis,weexploretheapplicationofguidanceindiffusion

models used for molecular generation. We analyze at the failure modes of using

a surrogate model to guide a diffusion model to generate molecules with stronger

bindingaffinity,andwebuildPolyGen2D,acontrolledtestenvironmentwherethese

modescanbeisolated.













































                                              2

## Page 13

2    Background



2.1    Notation



   Symbol        Meaning

   𝑃            Proteinpockettogetherwithitsatomfeaturesandcoordinates.
   𝑥0            Clean coordinates of the object being generated: ligand coordi-
                       natesinTargetDifforpolygoncoordinatesinPolyGen2D.
   𝑥𝑡            Noisycoordinatesatdiffusionstep  𝑡.
   𝑣𝑡            Discreteligandatom-typestateatdiffusionstep  𝑡 inTargetDiff.
   𝑡             Diffusiontimestep.
   𝛽𝑡 , 𝛼𝑡 ,      ̄𝛼𝑡       Noise variance, per-step signal retention, and cumulative signal
                       retention.
   𝜇𝜃(𝑥𝑡 , 𝑡)       Reverse-stepmeanimpliedbythedenoiser.
   ℎ(ℓ)𝑖            Hiddenembeddingofnode  𝑖atmessage-passinglayer  ℓ.
    ̂𝑎𝜙            Surrogate-predictedbinding-affinityscore.
   𝑔(𝑥𝑡 , 𝑡)         Arbitrarydifferentiableguidancescoringfunction.
   𝜆𝑡            Guidancestrength,includinganytime-dependentschedule.

                              Table2.1: Mainnotationused.


DetailedscheduleconstantsaredefinedinAppendix                  A.1.





















                                                3

## Page 14

2.2   Drug Discovery Context


Inthepast,Drugdiscoverywasaslowandexpensiveprocess. Researcherswould

identifyabiologicaltarget,manuallydesignorscreenmoleculesagainstit,andthen

testthosemoleculesoverstagesofcomputationalandexperimentalevaluation[4].

Althoughvastlibrariesofknowncompoundsexist,thenearlyinfinitecombinatorial

spaceofpossiblemoleculesmeantthatthisprocesswasconstrainedbyhowmany

moleculescouldrealisticallybetested[5].


Machine learning introduces the possibility of generating candidate molecules in-

stead of only screening preexisting ones. A generative model can learn the dis-

tribution of realistic molecules and then sample new ones that match the patterns

presentinthetrainingdata[6,       7]. Intarget-awaredrugdiscovery,thegoalbecomes

togeneratemoleculesthatarenotmerelyrealistic,butarelikelytobindtoaspecific

proteinpocket[1,    8].


The task of this thesis is to understand whether the sampling of diffusion models

for molecular generation can be improved using guidance from an external scor-

ing function [9]. That question is important because in a realistic drug-discovery

pipeline, binding is only one of several relevant objectives [5]. Ideally, a useful

generative model should be steerable toward additional properties without having

toretraintheentiremodelfromscratch[4].







                                              4

## Page 15

2.3   p53 and the Y220C Mutation


Guardianp53isavitalproteinpresentineveryhumancell–itstasktoregulatethe

lifeanddeathofitshostcell[2,       10]. Afunctioningp53preventsmutatedcellsfrom

developingintolethaltumorsandstoppingcancerbeforeitcanform[2]. However,

if p53 itself becomes mutated and can no longer perform its crucial role, the cell

(andthustheentirebody)isleftvulnerable[10]. Amutationinp53hasbeenfound

to contribute to over 50% of all known cancers, so one can imagine the allure of

restoringthemutantguardian[2,        10].


This study will focus on the Y220C mutant of p53, but the method is relatively

target-agnostic [10]. Y220C is chosen because the molecule PK11000 has been

foundtorestoreit,andwhilePK11000isnotviableasatheraputicdrugduetoits

toxicitytothehumanbody,itservedasaproof-of-conceptthatfunctionalrestoration

of the mutant is achievable [2,    10]. The ultimate goal in this lab is a pipeline that

generatesmoleculesthatbindtoandrestorethetarget[10]. However,theredoesnot

yetexistarestorationscorethatcanbeuseddirectlyinsidethegenerativeprocess,

andthusthisthesisstudiesguidanceinthemoretractablesettingofbinding-affinity

optimization while treating restoration-oriented guidance as a future extension [2,

10].










                                              5

## Page 16

2.4   Molecular Docking


Toevaluatewhetherageneratedmoleculeislikelytobindtoatargetpocket,weuse

moleculardocking,acalculationthatquicklyestimateshowfavorablyaligandfits

intoaproteinbindingsite. Typically, adockingprogramtriestominimizethepo-

tentialenergyofthesystemandmapstheresulttoascalarscore,withalowerscore

implying better docking. Docking is useful because it is computationally cheap,

but it is still an estimate [4]. More importantly, it is not differentiable, meaning

wecannotcalculatehowtochangethemoleculeinordertominimizethedocking

score[5]. TheprimarydockingsoftwarewewilluseisthePythonimplementation

ofAutoDockVina[3].



2.5   Molecular Representation


Amoleculeisnaturallyrepresentedasagraph,withatomsformingthenodesofthe

graphandbondsformingtheedgescitepsternlieb2022targetspecific,alakhdar2024diffusion.

In three-dimensional generative modeling, each node also carries continuous geo-

metricinformationintheformofcoordinates,pairedwithdiscreteinformationsuch

asatomtype[1,     7,8].


Simplefixed-lengthvectorsarenotasufficientrepresentation,sincemoleculesvary

insize,havelocalstructure,andcontainmeaningintherelationshipsbetweenatoms

[10]. Thus,ausefulmoleculargenerativemodelmustutilizeboththediscreteand



                                            6

## Page 17

Figure2.1: Moleculerepresentedasagraph.


continuousinformationofthemoleculewhilestillremainingsensitivetothegeom-

etryofthesystem[4,     7, 8].


In our setting, the molecule’s quality depends on the protein pocket in which it is

meanttobind,sothegenerativemodelmustrepresenttheprotein-ligandcomplexin

awaythatallowsthelocalandglobalcontextofthepockettoinfluencethemolecule

beinggenerated[1,    4].



2.6   Deep Neural Networks


Neural networks take an input representation, transform it through a sequence of

learnedlayers,andproduceanoutputsuchasadenoisedsample,ahiddenembed-

ding,orascalarscore[7,     10]. Forourpurposes,thesearepowerfultoolsthatwecan

useasfunctionapproximators. Adeepneuralnetworkisaparameterizedfunction

withenoughflexibilitytolearncomplicatedmappingsfromdata[11].


Thebasiccomputationinonelayerisanaffinetransformationfollowedbyanon-




                                            7

## Page 18

linearity:

                               ℎ(ℓ+1)  =  𝜎(𝑊 (ℓ)ℎ(ℓ)  +  𝑏(ℓ)) .


Here,  ℎ(ℓ) istherepresentationatlayer  ℓ,  𝑊 (ℓ) and  𝑏(ℓ) arethelearnedweightsand

biases,and  𝜎isanonlinearactivationfunctionsuchasReLUorSiLU.


Stackingmanysuchlayersyieldsadeepmodel



                                            ̂𝑦  =  𝑓𝜃(𝑥),



where  𝑥istheinput,     ̂𝑦istheprediction,and  𝜃denotesthefullcollectionoflearned

parameters.


Trainingmeanschoosing  𝜃sothatpredictionsmatchthedesiredtargetsonexample

data. Incompactform,thisiswrittenas



                                              𝑁
                                ℒ(𝜃)  =    1𝑁∑   ℓ(𝑓𝜃(𝑥𝑖), 𝑦𝑖) .
                                             𝑖=1


where  (𝑥𝑖, 𝑦𝑖) is the  𝑖th training example,  ℓ is the error function for one example,

and  ℒistheaveragetraininglossthatoptimizationtriestominimize.


Inpractice,theparametersareupdatedbyanoptimizersuchasgradientdescentor

oneofitsvariants. Abasicgradientdescentstepis



                                    𝜃  ←  𝜃  −  𝜂∇𝜃ℒ(𝜃).




                                               8

## Page 19

where  𝜂isthelearningrate,whichcontrolsthestepsize,and  ∇𝜃ℒ(𝜃)isthegradi-

ent of the loss with respect to the parameters. In this thesis, these calculations are

abstractedawayinpracticebyPyTorchanditsautomaticdifferentiationtools[12].

However, the underlying idea is conceptually important: subtracting the gradient

withrespecttoparametersmovestheminadirectionthatdecreasestheloss,while

addingthegradientwithrespecttosomevariablemovesthatvariableinadirection

thatincreasesthequantitybeingdifferentiated. Thissameintuitionlaterappearsin

guidance, where gradients are taken with respect to the current sample rather than

withrespecttothemodelparameters[13,            14].


Latermodelsdiffermainlyinhowtheyrepresenttheinputandhowtheystructure

the layers: a multilayer perceptron applies dense layers to vectors, a graph neural

networkaddsmessagepassingovernodesandedges,andadiffusiondenoiseruses

thesamegeneraltraininglogicbutwithtargetsdeterminedbythediffusionprocess

[1,6].



2.7   Graph Neural Networks


The fundamental challenge of machine learning is enabling the model to truly un-

derstandthemeaningofthedataitisintendedtolearnfrom. Thisproblemisknown

asrepresentationlearning,andtechniquesareconstructedbasedontheformatofthe

data – convolutional neural networks to understand grid-like data, transformers to

understandsequencedata. Inourcase,wewillusegraphneuralnetworks(GNNs),



                                             9

## Page 20

whicharedesignedforgraph-structureddata. Inagraph,themeaningofanodede-

pendsonitsownfeaturesaswellasthenodesandedgessurroundingit[15]. GNNs

address this by using message passing, during which each node repeatedly aggre-

gates information from neighboring nodes and updates its internal representation

accordingly[16].


Amessage-passingupdatecanbewrittenas



             𝑚(ℓ)𝑖       =       ∑𝜓(ℎ(ℓ)𝑖     , ℎ(ℓ)𝑗     , 𝑒𝑖𝑗 ) ,               ℎ(ℓ+1)𝑖              =  𝜙(ℎ(ℓ)𝑖     , 𝑚(ℓ)𝑖     ) .
                      𝑗∈𝒩(𝑖)


where  𝒩(𝑖) is the neighborhood of node  𝑖,  𝑚(ℓ)𝑖  is the information gathered from

itsneighborsatlayer  ℓ,and  𝜓and  𝜙arelearnedupdatefunctions[16].


In general, GNN prediction tasks are done at the node level, edge level, or graph

level. For example, one might predict the type of a masked atom, the presence of

abond,oragraph-levelpropertysuchasbindingaffinity. Becausemoleculesvary

insizeandbecausetheirstructureisinherentlyrelational, GNNsareamuchmore

naturalfitthanstandardmultilayerperceptronsinmostrealisticmolecularsettings

[1,15].



2.8    SE(3)-Equivariance


Moleculesexistinthree-dimensionalspace,andtheirphysicalmeaningdoesnotde-

pendonanarbitrarychoiceofcoordinateframe[1,                 7]. Ifaprotein-ligandcomplex



                                               10

## Page 21

is rotated or translated in space, it is still the same complex [1,         8]. A target-aware

moleculargenerativemodelshouldthereforebehaveconsistentlyundersuchtrans-

formations[1,    4, 8].


This requirement is captured by the idea of SE(3)-equivariance. The Special Eu-

clideanGroupin3-Dimensions(SE(3))consistsofthree-dimensionalrotationsand

translations [1,  4,  7, 8]. A model is equivariant to these transformations if trans-

formingtheinputresultsinacorrespondingtransformationoftheoutputinsteadof

producing an unrelated change [1,         8]. This is desirable in our setting, because if

theproteinpocketisrotated,thegeneratedligandshouldrotatewithitinacoherent

way[1,   4, 8].


Mathematically,equivariancemeanstheoutputtransformswiththeinput.



                                   𝑓 (𝑅𝑥  +  𝑟)  =  𝑅𝑓 (𝑥)  +  𝑟,



Here,  𝑥 is the input geometry,  𝑓 is the model,  𝑅 is a rotation, and  𝑟 is a translation

[1,4, 8].


Inourcase,SE(3)-equivarianceisbeneficialbecausethegeometricrelationshipbe-

tween the protein and the ligand is important, but the absolute world-frame orien-

tation of the complex does not. A model that ignores this principle risks learning

meaninglessdependenciesonarbitrarycoordinatechoicesinsteadofpurechemistry

[1,4].




                                               11

## Page 22

2.9   Pre-Diffusion Approaches


PreviousmethodsusedbytheThayerLabtoapproachthistaskincludeactor-critic

autoregressive methods, though none have yet attempted a model that generates

moleculesthatbothbindtoandrestoremutantp53. TheodoreB.Sternlieb’sthesis

used deep reinforcement learning to fine-tune a pretrained generative model over

moleculargraphs,biasingitwithrewardfunctionsthatencouragedesirablemolec-

ularpropertiesandhighbindingaffinitytoatargetprotein[10].


Actor-criticmethodscouldbeextendedtorestoremutantp53,asanotherrewardcan

easilybewiredintotheRLfeedbackloop,andthiswouldbeapromisingapproach

if the method itself were not intrinsically flawed. The key to generative AI and

machine learning in general is properly representing and reflecting the structure

and behavior of your data, and, in this case, generating a molecule atom-by-atom

violatesthatbyimposinganartificialorderingontheatomsofthemolecule[1,                   4, 8].

Although realistic molecules can be formed using this approach, in general they

tendtobelessrealisticandmoreunstable[8]. Thus,currentstate-of-the-artmodels

useadifferentapproachentirelywhicheliminatesthisdefianceofnature: diffusion

[1,4, 8].












                                             12

## Page 23

2.10    Diffusion Models


Diffusionmodelsaregenerativemodelsthatlearntoreverseagradualnoisingpro-

cess[6,  7]. Startingfromacleandatapoint,noiseisrepeatedlyaddeduntilthedat-

apointistransformedintopureGaussiannoise[6,             7, 13]. Aneuralnetworkisthen

trainedtoreversethatprocessstepbystep,turningnoisebackintoarealisticsample

[6,7]..


Thismakesdiffusionanappealingframeworkforgeneration[6]. Sincethemodel

does not need to construct a sample all at once, during the early steps it can re-

covercoarsestructure,whilelaterstepsrefinedetails,abehaviorisveryapplicable

domainslikeimagegenerationandmoleculargeneration[6].


Historically,diffusioncanbeconnectedtoearlierlatent-variablegenerativemodels

such as variational autoencoders [6]. VAEs learn an encoder and decoder jointly,

mappingdataintoalatentprobabilitydistributionandthenreconstructingtheinput

from that distribution [6]. Diffusion simplifies this by fixing the forward corrup-

tionprocessandlearningonlythereversedenoisingprocess,leadingtomorestable

generationandsharpersamples[6,         13].



2.11    Denoising Diffusion Probabilistic Models


Thediffusionframeworkmostrelevanttothisthesisisthedenoisingdiffusionprob-

abilistic model (DDPM) [6,      7]. In a DDPM, a forward process gradually corrupts


                                            13

## Page 24

a clean sample into noise according to a fixed schedule. The reverse model then

learnstopredicthowtoremovethatnoiseonestepatatime[6,                        7].


Aparameterizationcommoninimagegenerationimplementationstrainsthemodel

to predict the Gaussian noise that was added at a given timestep, called the   𝜖-

predictionparameterization[6,        13]. Anothermathematicallyequivalentparameter-

izationknownasthemean-prediction(𝑥0-prediction)predictsthedenoisedsample

directly [6]. In our geometric setting, the mean-prediction is more effective, since

it allows the model to focus on learning the overall structure of each clean data-

pointratherthanthefine-grainedadjustmentsneededinperfectingeachpixelofa

generatedimage[1,       4, 8].


Theforwardcorruptionstepcanbewritteninclosedformas



                       𝑥𝑡  =  √  ̄𝛼𝑡  𝑥0  +  √1  −      ̄𝛼𝑡  𝜖,               𝜖  ∼  𝒩(0, 𝐼 ),



when  𝑥0 isthecleansample,  𝑥𝑡 isitsnoisyversionatstep  𝑡,      ̄𝛼𝑡 controlshowmuch

signalremains,and 𝜖isGaussiannoise. Thelearnedreversestepthensamplesfrom



                                 𝑥𝑡−1  ∼  𝒩(𝜇𝜃(𝑥𝑡, 𝑡), 𝜎2𝑡  𝐼 ).



when  𝜇𝜃(𝑥𝑡, 𝑡) is the denoiser’s estimated step back toward the data distribution,

and  𝜎𝑡 setshowmuchrandomnessisstillinjected[6,                 7]..






                                               14

## Page 25

Thetwocommonpredictionparameterizationsareconnectedby


                             ̂𝑥0,𝜃(𝑥𝑡, 𝑡)  =   𝑥𝑡  −  √1  −      ̄𝛼𝑡      ̂𝜖𝜃(𝑥𝑡, 𝑡).
                                                      √  ̄𝛼𝑡


when      ̂𝜖𝜃isthemodel’spredictednoiseand     ̂𝑥0,𝜃isthecorrespondingestimateofthe

originalcleansample[6].



2.12    Guidance in Diffusion Models


Anattractivefeatureofdiffusionmodelsisthattheirsamplingprocesscanbemod-

ified without retraining the base denoiser. In classifier guidance, for example, a

separate model is trained to predict class labels from noisy inputs. During reverse

diffusion,thegradientofthatclassifierwithrespecttothecurrentsampleisusedto

shiftthereversesteptowardhigherprobabilityunderthetargetclass[13,                      14,  17].


Inprinciple,anydifferentiablescoringmodelcanbeusedtoguidereversediffusion

in any domain. One can imagine steering samples toward higher affinity, higher

synthesizability, or any other property that can be evaluated on the current noisy

state[1,  4, 5, 9].


Inthatcase,agenericguidedreverseupdatetakestheform



                       𝑥𝑡−1  ∼  𝒩(𝜇𝜃(𝑥𝑡, 𝑡)  +  𝜆𝑡∇𝑥𝑡 𝑔𝜙(𝑥𝑡, 𝑡), 𝜎2𝑡  𝐼 ),



when 𝑔𝜙istheexternalscore, ∇𝑥𝑡 𝑔𝜙pointsinthedirectionthatimprovesthatscore,


                                               15

## Page 26

and  𝜆𝑡 controlshowstronglyguidanceaffectsthestep[5,             13, 17].


Inthisstudy,weexploretheapplicationofguidanceindiffusionmodelsinmolecular

generation.

















































                                             16

## Page 27

3   Methods



3.1   Overview


Thisthesisstudiesguidanceintwosettings. WeevaluateguidancedirectlyinTar-

getDiff,atarget-awaremoleculardiffusionmodeltrainedtogeneratemoleculesin-

sideaproteinpocket[1,      4]. WethenintroducePolyGen2D,acontrolledsynthetic

testbeddesignedtoisolatethemechanicsofguidanceinasimplercoordinate-based

diffusion setting. TargetDiff is the real target-aware molecular model of interest,

butitcontainsmanyinteractingsourcesofcomplexity[1,              8]. PolyGen2Dremoves

manyofthoseconfoundingfactorssothatspecificquestionsaboutguidancecanbe

studiedmoredirectly.


We first generate and evaluate molecules using TargetDiff, then train a surrogate

affinitymodelandtestitsuseforsampling-timeguidance. Inordertomorereliably

improvegeneration,weintroducePolyGen2Dtostudyguidanceinacontrolledset-

ting.
















                                            17

## Page 28

Figure3.1: TargetDiffDiffusionProcess[1]


3.2   TargetDiff Pipeline



3.2.1  Model Setup


TargetDiffisadiffusionmodelbasedontheDDPMframeworkthatgeneratesmolecules

inthreedimensionsconditionedonaproteinpocket. Itistrainedonadatasetofmil-

lionsofprotein-ligandcomplexesandisdesignedtoproduceligandstructuresthat

fit inside a target pocket while respecting the geometric structure of the protein-

ligandenvironment.


For the purposes of this thesis, TargetDiff is treated as a frozen pretrained genera-

tivemodel. Wedonotretrainthemodelitself. Instead,weuseitastheunderlying

denoiserandaskwhetheritssamplingprocesscanbeimprovedbyinjectinganad-

ditionalguidancesignalderivedfromaseparatescoringmodel. Weaskwhethera

strongexistingtarget-awarediffusionmodelcanbesteeredatsamplingtimewithout

changingitscoregenerativebackbone.


Ourproteinofinterestismutantp53Y220C.Becausep53isnotpartoftheoriginal



                                            18

## Page 29

training distribution in any direct supervised sense, this setting also tests whether

the learned molecular prior in TargetDiff generalizes well enough that meaningful

pocket-awaregenerationispossibleforanewtargetofinterest.



3.2.2  Candidate Generation and Evaluation


WefirstuserawTargetDifftosamplealargecollectionofcandidatemoleculesfor

the Y220C pocket. These generated molecules are then postprocessed and evalu-

ated. Theprimaryquantitativeevaluationisdockingscore,obtainedusingAutoDock

Vina[3]. Inadditiontodocking,wefiltergeneratedmoleculesusingsimplecriteria

suchasQEDandsynthesizabilitytoremovelow-qualitysamples.


Thisstageservesasabaselineevaluationandasthesourceoflabeleddatafortrain-

ingthesurrogateaffinitypredictor.



3.3   Surrogate Guidance (Molecular)



3.3.1  Dataset Construction


The surrogate dataset is constructed from TargetDiff-generated molecules labeled

withdockingscores. Trainingonmodel-generatedsamplesensuresthatthepredic-

torisalignedwiththedistributionproducedbythebasemodelagainstourchosen

pocket.





                                            19

## Page 30

3.3.2   Surrogate Model


Wedesignedthearchitectureofasurrogateaffinitymodelasagraphneuralnetwork

builtoveraprotein-ligandgraphcontainingligand-ligandedgesandligand-protein

edges. Nodefeaturesconsistprimarilyofatomtypes, whileedgesareconstructed

from spatial proximity and augmented with edge features such as edge type and

distance. Aftermessagepassing,ligandnoderepresentationsarepooledandpassed

throughanMLPtoproduceascalarbinding-affinityprediction.


Thesurrogatealternatesmessagepassingwithaligand-levelreadout:


     ℎ(ℓ+1)         ℎ(ℓ)         𝜓(ℎ(ℓ)                ,                    ̂𝑎𝜙  =MLP⎛⎜1ℎ(𝐿)
      𝑖              =  𝜙⎛⎜⎜𝑖     ,      ∑𝑖     , ℎ(ℓ)𝑗     , 𝑒𝑖𝑗 )⎞⎟⎟        |𝐿|  ∑    𝑖      ⎞⎟
                  ⎝      𝑗∈𝒩(𝑖)                      ⎠                      ⎝     𝑖∈𝐿      ⎠ .


where  ℎ(ℓ)𝑖  is the hidden representation of atom  𝑖 at layer  ℓ,  𝐿 is the set of ligand

atoms,and      ̂𝑎𝜙 isthesurrogate’spredictedaffinity.


In our case, the choice of a GNN stems from the structure of the problem. Bind-

ing affinity depends on both the local geometry of the ligand and its interactions

with the surrounding protein atoms. A graph model over the joint protein-ligand

environmentisthereforeanaturalwaytorepresentthenecessaryinformation.



3.3.3   Guidance Mechanism


Once trained, the surrogate model is inserted into the reverse diffusion process as

aguidancefunction[5,        13,  18]. Duringsampling, thecurrentnoisyligandstate  𝑥𝑡


                                                20

## Page 31

is passed into the surrogate model, and the gradient of the predicted affinity with

respect to the ligand coordinates is used to bias the reverse step [1,              5,  13]. The

intendedeffectisthatifthesurrogatepredictsthatasmallmovementofthecurrent

samplewould increase the final affinityscore, then thatdirection should be added

tothereversedenoisingupdate[5,            9, 13].


Usingthatsurrogate,thesampling-timeperturbationcanbewrittenas



 Δ𝑡  =  𝜆𝑡∇𝑥𝑡(−    ̂𝑎𝜙(𝑥𝑡, 𝑃)),               𝑥𝑡−1  =  𝜇𝜃(𝑥𝑡, 𝑡, 𝑃)  +  Δ𝑡  +  𝜎𝑡𝑧,               𝑧  ∼  𝒩(0, 𝐼 ).



Δ𝑡 istheguidanceshiftaddedattime  𝑡,  𝑃denotestheproteinpocketcontext,and  𝑧

isfreshGaussiannoiseusedtokeepsamplingstochastic[1,                     5, 6].


Conceptually, this is the same basic logic as classifier guidance in image diffu-

sion. Thediffusionmodelweightsareleftunchanged. Onlythesamplingprocessis

modified,byaddingagradienttermderivedfromanexternaldifferentiablemodel

[4, 5, 13].




















                                                21

## Page 32

3.4    PolyGen2D Testbed



3.4.1   Motivation




                                            Synthetic
                                            Polygon
                                              Data



                                    Train  Diffusion  Model




                                       Sample  Polygons




                              Optional  Differentiable  Guidance



                                     Measure  What  Works
                                          Architecture
                                            Strength
                                            Schedule



                             Use  the  Design  Rules  in  TargetDiff

               Figure3.2: PolyGen2D-to-TargetDiffresearchworkflow.


Themolecularsettingintroducesmultiplesourcesofcomplexity,includingvalidity

constraints, mixed discrete and continuous representations, and distribution shift

acrossdiffusionsteps[1,      5, 7, 8]. Thesefactorsmakeitdifficulttoisolatetheeffect

ofguidance.



                                               22

## Page 33

While our eventual goal is to integrate guidance into a TargetDiff-like model, we

firstbuildaworkingprototype anduseitasa blueprintforthereal version. Poly-

Gen2Dservesasacontrolledsynthetictestbeddesignedtoisolateandevaluateguid-

anceincoordinate-baseddiffusionmodelsongraph-structureddata.



3.4.2   Data and Representation


We construct synthetic polygon datasets, beginning with fixed-size near-regular

hexagonsandextendingtovariable-sizedpolygonswithdifferingnoiselevels. The

data distribution and target properties are fully controlled, and labels can be com-

putedanalytically.



3.4.3   Diffusion Models


ThebasePolyGen2DmodelisaclassicDDPMoverpolygoncoordinates. Webegin

withanMLPdenoisertrainedonadatasetof100,000near-regularhexagons. After

training,wesample10,000hexagonsfromthefrozenmodel,scoreboththetraining

and sampled polygons using a regularity metric, and compare the resulting distri-

butions. Ideally, the generated distribution should match the training distribution

[6,7, 13].


Thesyntheticdiffusionmodelusesthesamebasiccorruptionandtrainingtemplate:



             𝑥𝑡  =  √  ̄𝛼𝑡  𝑥0  +  √1  −      ̄𝛼𝑡  𝜖,               ℒ(𝜃)  =  𝔼[∥    ̂𝑢𝜃(𝑥𝑡, 𝑡)  −  𝑢∥22] ,



                                               23

## Page 34

where  𝑥0 isthecleanpolygon,  𝑥𝑡 isitsnoisyversion,and  𝑢iswhichevertargetthe

denoiser is trained to predict, either the clean polygon itself (𝑥0-prediction) or the

addednoise(𝜖-prediction)[6,        13].


Becausethepolygondataaregraph-structured,wealsoimplementGCNandGAT

variantsofthedenoiser[19]. WealsoextendPolyGen2Dtovariable-sizepolygons.



3.4.4   Guidance Objectives



         Noisy  Sample
                𝑥𝑡


       Denoiser  Predict           Differentiable  Objective              Schedule
                ̂𝑥0,𝜃                       𝑔(𝑥𝑡 , 𝑡)                        𝜆𝑡




         Reverse  Mean                           Add  Guidance
            𝜇𝜃(𝑥𝑡 , 𝑡)                          𝛽𝑡  𝜆𝑡  ∇𝑥𝑡 𝑔(𝑥𝑡 , 𝑡)̃





                                                  Next  Sample
                                                      𝑥𝑡−1

                  Figure3.3: OneguidedreversestepinPolyGen2D


Guidance is implemented using differentiable polygon-level objectives. For the

baselinePolyGen2Dguidanceexperiments,theobjectiveisachosenscorethatcan

beevaluatedonintermediatenoisystatesanddifferentiatedwithrespecttothecur-

rentpolygoncoordinates[13,        17].




                                              24

## Page 35

Guidancemodifiesthereversestepas



            𝑥𝑡−1  =  𝜇𝜃(𝑥𝑡, 𝑡)  +       ̃𝛽𝑡𝜆𝑡∇𝑥𝑡 𝑔(𝑥𝑡, 𝑡)  +  √𝛽𝑡  𝑧,               𝑧  ∼  𝒩(0, 𝐼 ).̃



Whenoptimizingformoreregularpolygons,  𝑔(𝑥𝑡, 𝑡)  =  𝑠𝑟𝑒𝑔(𝑥𝑡)isthecurrentpoly-

gon’sregularityscore,  ∇𝑥𝑡 𝑠𝑟𝑒𝑔(𝑥𝑡)pointstowardmoreregularshapes,and       ̃𝛽𝑡scales

the correction by the reverse-time noise level. In the case of optimizing pocket-

conditioned experiments, PolyGen2D uses a differentiable pocket-fit score with

𝑔(𝑥𝑡, 𝑡)   =   𝑠𝑓 𝑖𝑡 (𝑥𝑡) and  ∇𝑥𝑡 𝑠𝑓 𝑖𝑡(𝑥𝑡) pointing towards polygons that fit better. When

usinganeuralnetworkapproximation,  𝑔(𝑥𝑡, 𝑡)  =  𝑠𝑓 𝑖𝑡 𝜙(𝑥𝑡). Thisscoreactsasageo-

metricproxyforwhetherapolygonoccupiesapocketbysamplingpointsalongthe

polygonboundary,rewardingsamplesthatremaininsidethepocket,andpenalizing

spillover,mismatchedsize,andunrealisticclearance. Appendix                   A.12–13    provides

aprecisedefinitionforeachoftheguidanceobjectives.



3.4.5   Surrogate Variants


PolyGen2Dalsoallowsguidanceexperimentsthatwouldbedifficulttorundirectly

in the molecular setting. We compare surrogates trained on clean polygon states,

surrogates trained on noisy polygon states, and surrogates trained on noisy states

together with the timestep parameter. This allows us to directly compare the per-

formanceofthesetrainingregimes.


Thenoisy-statesurrogateistrainedbycorruptingpolygonsandregressingtheclean


                                               25

## Page 36

regularityscore:



      𝑥𝑡  =  √  ̄𝛼𝑡  𝑥0  +  √1  −      ̄𝛼𝑡  𝜖,               ℒreg(𝜙)  =  𝔼𝑥0,𝑡,𝜖[(   ̂𝑦𝜙(𝑥𝑡, 𝑡)  −  𝑠(𝑥0))2].



with     ̂𝑦𝜙(𝑥𝑡, 𝑡)thesurrogate’spredictedscoreforanoisypolygonattime 𝑡,and 𝑠(𝑥0)

thecleanpolygonscoreitistrainedtorecover.



3.5   Experimental Design



3.5.1  TargetDiff Experiments


ThemolecularexperimentsbeginwithbaselinegenerationusingrawTargetDiffon

theY220Cpocket[1,        2]. Wethenevaluategeneratedcandidateswithdockingand

filteringcriteriaandusethatevaluateddatasettotrainthesurrogateaffinitypredic-

tor. Finally,werunguidedsamplingexperimentsinwhichthesurrogateisinserted

into reverse diffusion and the resulting samples are compared with the unguided

baseline.



3.5.2  PolyGen2D Experiments


Thesyntheticexperimentsaredesignedtoisolatespecificquestionsthatarehardto

answerdirectlyinthemolecularsetting. Theseinclude: howdenoiserarchitecture

changesthelearneddistribution,whetherguidancechangesthescoredistributionin

theintendeddirection,whetherclean-statesurrogatesdifferfromnoisy-statesurro-


                                              26

## Page 37

Denoiser Architecture        Guidance Strength            Guidance Timing             Guidance Model

      MLP vs GCN vs GAT           how much guidance?            when to guide?            noisy-state surrogate?





                                                 Design Rules for
                                              Differentiable Guidance




                                                      Goal:
                                      plug differentiable guidance into TargetDiff

                              Figure3.4: PolyGen2Dmethodology


gates,andwhetherincludingthetimestepimprovesguidancequality.



3.5.3    Evaluation Metrics


In the molecular setting, the primary evaluation criteria are docking score, drug-

likeness, synthesizability, and visual inspection of top-ranked candidates. In the

polygonsetting,theprimarycriteriaarethevisualqualityofsampledpolygonsand

thecomparisonbetweentrainingandgenerateddistributions.























                                                      27

## Page 38

4   Results




























                 Figure4.1: DockedgeneratedmoleculeonY220C



4.1   Baseline TargetDiff


The first stage of this work was to evaluate the baseline TargetDiff model on the

Y220Cpocketwithoutanyaddedguidance. Usingthepretrainedtarget-awaredif-

fusionmodel,wegeneratedalargecollectionofcandidatemoleculesforthepocket

of interest and then evaluated those candidates using molecular docking. This es-

tablishedabaselineforwhattheunguidedmodelcouldalreadyachievebeforeany

attemptwasmadetosteersamplingtowardimprovedaffinity.


                                           28

## Page 39

Figure4.2: Scoredistributionofgeneratedmolecules


We successfully generated and scored over 10,000 molecules in our pocket of in-

terest on Y220C. We filtered the molecules to accept minimum QED and synthe-

sizabilityscores,thenrankedthembybindingaffinityscoreandvisualizedthetop

candidates.


Figure  4.1  shows an example generated molecule docked in the Y220C pocket,

whileFigure    4.3 showsseveralofthetop-rankedgeneratedcandidates.












                         Figure4.3: Topgeneratedcandidates



                                             29

## Page 40

The results in Figure    4.2 show that raw TargetDiff is already capable of produc-

ingplausibletarget-awarecandidatesforY220C.Moleculeswithabindingaffinity

score ≥  8kcal/molareconsideredpromising,butthebestmoleculesintheliterature

stillscorebetterthantheonesgeneratedwithrawTargetDiff.



4.2   Surrogate Predictive Performance


WetrainedasurrogatemodelonmoleculesgeneratedbyTargetDiff[1]andlabeled

byAutoDockVina[3],andevaluateditonaheld-outtestset.

























           Figure4.4: Surrogateaffinitymodelstandaloneperformance.


Although we evaluate the binding affinity of our final molecules using the Vina

Dock score, which performs a minimization search to find the optimal pose of

the molecule before scoring its affinity [3], we were careful to label it on the raw

                                             30

## Page 41

score_onlyVinalabel,sincethisallowsthemodeltolearnthepredictiongivenits

current3Dorientationinthepocket,notsomeotherarbitraryorientationfoundby

theVinaDockalgorithm. ThisallowsthepositionalcontextthattheGNNextracts

tomoreeffectivelyinformthemodel’sprediction.


Thesurrogatemodellearnedtocorrectlypredictthebindingaffinityofamolecule,

asshownintheparityplotofthetestsetinFigure           4.4. Oncleanevaluatedmolecules,

themodellearnedarelationshipbetweenmolecularstructureanddockingscore.



4.3   Guided PolyGen2D Performance



              Type  Scale  Start  End           𝑁   Score-only  Δ  Dock  Δ
              𝜎     20   0.05  0.02  191    -0.013                  -0.079
              𝜎     10   0.05  0.02  191    -0.004                  -0.077
              fixed   0.2   0.05  0.02  191    -0.033               -0.069
              𝜎     50   0.10  0.02  191    -0.018                  -0.048
              𝜎      8    0.10  0.02  191    -0.014                 -0.045
              fixed   0.2   0.10  0.02  190     0.011               -0.015
              𝜎     10   0.10  0.02  191    -0.019                   0.054
              𝜎     20   0.10  0.02  191    -0.020                   0.061
              𝜎      8    0.05  0.02  191    -0.002                  0.070
              fixed   1.0   0.05  0.02  178     0.146                0.116
              fixed   1.5   0.05  0.02  169     0.235                0.170
              fixed   0.5   0.10  0.02  184     0.161                0.171
              fixed   0.5   0.05  0.02  189     0.012                0.205
              fixed   1.5   0.10  0.02  158     0.390                0.217
              fixed   1.0   0.10  0.02  161     0.321                0.227
              𝜎     50   0.05  0.02  191    -0.030                   0.228

                          Table4.1: Guidedminusbaseline.


LowerisbetterforVinametrics[3]. Cellcolorencodesdockverdict: greenwork-

ing,yellow=mixed,red=notworking.



                                            31

## Page 42

Weconductedasweepacrosshyperparameterstotrytoisolateamodeforwhichthe

averagedockingscoreimprovedwiththeguidancemodelcomparedtothebaseline

model. Table  4.1 showsthatwhenthesurrogatewaspluggedintothereversediffu-

sionprocessunderspecifichyperparamters,itledtoanimprovementinthebinding

affinityofthegeneratedmolecules.



4.4   PolyGen2D Baseline Behavior


WebeganbytrainingPolyGen2Donfixed-sizenear-regularhexagons. Aftertrain-

ing, we sampled a large set of polygons from the frozen model and compared the

scoredistributionofthegeneratedpolygonswiththescoredistributionofthetrain-

ingpolygonsusingaregularitymetric.

           GCN                           GAT                           MLP



















     Figure4.5: PolyGen2Dunguidedfixed-sizeresultsacrossarchitectures.


Beforeguidance,themodelproducedreasonableoutputs,butthedistributionofthe


                                          32

## Page 43

scoredtrainingdatadidnotmatchthedistributionofthescoredsampleddata,and

somearchitecturesmatchedthedistributionbetterthanothers,asseeninFigure                4.5.

Thespikenear0.0intheGCNscoredistributionisconsistentwiththemanyoutliers

shownonthePCAplot. TheGAThasfarfeweroutliers,withtheMLPhavingthe

leastamountofoutliers. SeeAppendix         A.8 fordetailsofthedenoiserformulations.



4.5   Guidance in PolyGen2D














               (a)Unguided                                     (b)Guided

          Figure4.6: PolyGen2Dunguidedvs. guided(fixed-sizedMLP)


Wethenaddedguidanceintheformofadifferentiablescoringfunctionthatcalcu-

latestheregularityofapolygon. Figure        4.6 showsthatwithguidanceenabled,the

scoredistributiondrasticallyshiftedtofavorhigher-scoringpolygons.



4.6   Surrogate Variants


In the case of predicting binding affinity in the molecular domain, a differentiable

guidancefunctionisintractableandasurrogateneuralnetworkapproximatorisin-

stead required to use as a differentiable guidance function. Although our   𝑠𝑓 𝑖𝑡 in

                                            33

## Page 44

PolyGen2Disdesignedtobedifferentiable,wesimulatetheintractabilitybytrain-

ing a surrogate model  𝑠𝑓 𝑖𝑡 𝜙 to predict polygons labeled by  𝑠𝑓 𝑖𝑡, and then compare

the performance of a diffusion model guided by surrogates trained under different

conditions.




















               Figure4.7: PolyGen2DGuidedSamplingPerformance


Figure  4.7 demonstrates that surrogates trained on noisy states outperform clean-

statesurrogateswhenusedforguidance. Includingtimestepinformationasafeature

oftheneuralnetworkfurtherimprovesperformance.



4.7   Architectural Results


Figure  4.5 shows an unexpected architectural result produced by PolyGen2D. Be-

causethesyntheticdataaregraph-structured,weinitiallyassumedthatagraphneu-

ral network would be the natural and superior denoiser architecture. We therefore

implementedbothGCNandGATvariantsinadditiontothebaselineMLPdenoiser.

                                             34

## Page 45

Inthefixed-sizeregular-hexagonsetting,however,performanceactuallydecreased

withtheGCN,andtheGATwascomparablebutthePCAprojectionshowedthatit

sufferedfromslightlymoreoutlierscomparedtotheMLP.

















































                                         35

## Page 46

5   Discussion



5.1   Core Finding


Theresultssupportthatyes,adiffusionmodelformoleculargenerationcanbeim-

proved at sampling time by applying guidance from an external scoring function.

In the molecular setting, guidance was capable of improving affinity under some

hyperparametersettings,butthosegainsweremodestandnotrobustacrossthefull

sweep. In the synthetic setting, by contrast, guidance produced much clearer im-

provements. Together,theseresultssuggestthatsampling-timeguidancecanwork,

butthatitseffectivenessdependsstronglyonhowwelltheguidancesignalmatches

thestatesencounteredduringreversediffusion.


The molecular experiments show that a clean-state surrogate can produce a useful

signalinsomecases, butnotaconsistentlystrongone. Thesyntheticexperiments

showthatwhentheguidanceobjectiveistrainedwiththedatafromwithinthenoisy

diffusionprocessinmind,theeffectbecomesmuchmorepronounced.



5.2   Why Molecular Gains Remain Limited


Inseveralsettings,guidedsamplingimprovedaverageaffinityrelativetothebase-

line. However, these improvements were small and sensitive to hyperparameter

choice,ratherthanbroadandreliable.


                                            36

## Page 47

Previous attempts were done inserting guidance early on in the diffusion process,

which broke the model’s ability to bring molecules back to the realistic manifold

andpreventeditfromgeneratingvalidmolecules.


Since the guidance model requires relatively clean data as input to function at all,

thismeansthatguidancecanonlybeinsertedintotheveryendofthefulldiffusion

processoncethedataitisseeingiscleanenough, andacttomakesmallimprove-

mentsonthemodelinsteadofmajorstructuralimprovemetsthatitmightotherwise

beabletomakeearlyon.



















         Figure5.1: Overlayofguidedandunguidedgeneratedmolecules.


InFigure  5.1  thetealmoleculeisunguided,whiletheredmoleculeisguided.


AlikelyreasonisacommonMLfailuremode: distributionmismatch. Thesurro-

gateistrainedoncleanmolecularstates,butduringreversediffusionitisevaluated

onnoisyintermediatestates. Evenifthesurrogatepredictsaffinityreasonablywell

oncompletedmolecules,itsgradientsbecomelessusefulwhenappliedtopartially

                                            37

## Page 48

denoisedsamplesthatlieoutsideitstrainingdistribution. Thus,guidancemaystill

pushsamplesinafavorabledirection,buttheeffectistooweakorunstabletopro-

duceastrongsystematicgain.



5.3   What PolyGen2D Clarifies


Inthemolecularsetting,manyfactorsareentangled,e.g. chemicalvalidity,mixed

discrete and continuous structure, docking noise, and the mismatch between clean

andnoisystates. Inthesyntheticsetting,weusedPolyGen2Dtoremovedorcontroll

these,makingitpossibletotestguidancemoredirectlyandinterprettheresultsmore

easily.


Inoursyntheticenvironment,analyticguidanceshiftedthescoredistributionstrongly

intheintendeddirection,andsurrogate-basedguidanceimprovedmoreeffectively

whenthe surrogatewas trained onnoisy states ratherthan only onclean ones. In-

cluding timestep information improved it further. These results support the idea

thatthemainobstacleinthemolecularsettingisbuildingaguidancemodelthatis

reliableacrossthediffusiontrajectory.



5.4   Architectural Considerations


ThePolyGen2Dexperimentsalsoproducedanarchitecturalresultworthinterpret-

ing carefully. In the fixed-size regular-hexagon setting, the MLP denoiser outper-

formed both GCN and GAT variants. This suggests that the denoising task in that

                                             38

## Page 49

toysettingdependsmoreonimmediateaccesstothefullglobalconfigurationthan

onlocalrelationalmessagepassing.


Thatresultshouldnotbeovergeneralized. Moleculesarevariable-sizeobjectswhose

behavior depends heavily on local geometric interactions, so the case for graph-

basedandequivariantmodelsinmoleculargenerationremainsstrong. Thistellus

thatthebestdenoiserdependsonthestructureofthetask.



5.5   Implications for Molecular Guidance


In the future a stronger guidance model would likely need to be trained on noisy

molecular states rather than only on clean states, and it would likely benefit from

explicit timestep conditioning. thus optimized for the reverse-diffusion regime in

whichitwillbeused.


Thepracticaldifficultyisthatnoisymolecularstatesaremuchhardertolabelthan

cleanones. Adistortedintermediatesamplemaynolongerbechemicallyvalidor

even processable by docking software. This makes the molecular problem more

challengingthanthesyntheticone.


Inaddition,ourcurrentsurrogatemodelonlymovesthecontinuouscoordinatesof

the molecule to optimize its objective and disregards the atom types. With only

late-stage guidance on the coordinates, the model won’t alther the distribution of

moleculesthattheunguideddenoiserwouldhaveotherwisecreated,sincethegen-

erationtrajectorywon’tbesignificantlyalteredbytheguidanceandwillinsteadact


                                             39

## Page 50

asalocalcoordinaterefinementmechanism.


Thereisajustificationforonlyoptimizingcoordinates–partlysinceanatomtype

vectorrepresentedusingone-hotvectorsisnotdifferentiable. Duringeachstepof

the diffusion sampling process, the model attempts to predict the final atom types

𝑣0 given  𝑣𝑡, which it outputs as a probability distribution and then samples it into

acategoricalchoiceofatomtype. Ifweusethesmoothprobabilitydistributionas

inputtoouraffinitymodel,themodelwilllikelysufferfromthesamedistribution

mismatchasitdidinthecaseofreceivingnoisycoordinateinputsifitwastrainedon

moleculeswithfixedatomtypes. Ifwesoftentheone-hotatom-typevectors,asmall

nudgeinthevectorwilllikelynotaffectthetypeoftheatom. Ifthegradientwasable

tonudgeittoflipanatomtype,thatmayresultinadrasticchangeintheprediction

score. Apotentialfutureareaofexplorationistocomputethegradientw.r.t. thesoft

distribution,usethatgradienttoadjustthetypelogitsafterapredictionofthelogits

𝑣0andbeforesampling,thensamplefromtheadjustedcategoricaldistribution. But

this is still less principled than coordinate guidance since the gradient occurs in

continuousspace,afterwhichaseparatediscontinuousactionisperformed.


Evenso,theseresultsindiactethatguidanceisworthpursuing,andidentifyandthat

aguidancemodelwhosesupervisionmatchesthestatesvisitedduringsamplingis

mosteffective.









                                            40

## Page 51

6   Conclusion



6.1   What This Thesis Establishes


Molecularguidanceproducedmodest,hyperparameter-sensitivegains,whileguid-

anceinPolyGen2Dwasmuchstrongerandmorereliable. Thissuggeststhatguid-

ancequalitydependsonalignmentbetweentheguidancemodelandthenoisystates

seenduringreversediffusion.



6.2   What Remains Open


Thelong-termgoalofthislabistoguidemoleculargenerationtowardsrestorationof

mutantproteinfunction. Althoughstilloutofourreach,thisthesisbringsuscloser

by providing a precise understanding of the difficulties of guidance in this setting

and how to make it more likely to succeed. We hope that our results and method-

ologieswillbeappliedinthefutureasthisnoblegoalbecomesmoreachievable.


















                                           41

## Page 52

Appendix A: Mathematical Details



A.1 Scope


Thisappendixcollectsthemathematicaldetailsmostrelevanttothethesis. ForTar-

getDiff,theimportantformulasaretheforwardandreversediffusionprocesses,the

direct  𝑥0 parameterization used for ligand coordinates, and the SE(3)-equivariant

refinement update. For PolyGen2D, the important formulas are the DDPM setup,

theconfigurablepredictiontarget,theguidedreversemean,thedifferentiablepoly-

gon regularity objective, and the pocket-fit objective used in the synthetic pocket

experiments.


Thesharedschedulequantitiesusedthroughouttheappendixare



                  𝛼𝑡  =  1  −  𝛽𝑡,                    ̄𝛼𝑡  =  ∏𝛽𝑡  =  𝛽𝑡 1  −      ̄𝛼𝑡−11  −      ̄𝛼𝑡    .
                                               𝑠≤𝑡  𝛼𝑠,                     ̃



A.2 TargetDiff: Forward Diffusion


Lettheproteinpocketbe



                              𝑃  =  {(𝑥𝑃𝑖   , 𝑣𝑃𝑖  )}𝑁𝑃𝑖=1,               𝑥𝑃𝑖     ∈  ℝ3,







                                                 42

## Page 53

andlettheligandatdiffusionstep  𝑡 be



                       𝑀𝑡  =  [𝑥𝑡, 𝑣𝑡],               𝑥𝑡  ∈  ℝ𝑁𝐿×3,        𝑣𝑡  ∈  {0, 1}𝑁𝐿×𝐾 .




Forligandcoordinates,theforwarddiffusionprocessisGaussian:



                                𝑞(𝑥𝑡  ∣  𝑥𝑡−1)  =  𝒩(𝑥𝑡; √𝛼𝑥𝑡   𝑥𝑡−1, 𝛽𝑥𝑡 𝐼 ) ,



withclosed-formmarginal



                               𝑞(𝑥𝑡  ∣  𝑥0)  =  𝒩(𝑥𝑡; √         ̄𝛼𝑥𝑡   𝑥0, (1  −      ̄𝛼𝑥𝑡 )𝐼 ) ,



sothat

                            𝑥𝑡  =  √   ̄𝛼𝑥𝑡   𝑥0  +  √1  −      ̄𝛼𝑥𝑡   𝜖,               𝜖  ∼  𝒩(0, 𝐼 ).



Fordiscreteatomtypes,thediffusionprocessmixesthecleanone-hottypewiththe

uniformcategoricaldistribution:



                               𝑞(𝑣𝑡  ∣  𝑣0)  =Cat(𝑣𝑡  ∣      ̄𝛼𝑣𝑡 𝑣0  +  1  −      ̄𝛼𝑣𝑡𝐾     1) .













                                                          43

## Page 54

A.3 TargetDiff: Reverse Process and Direct  𝑥0 Prediction


Thereverse-timeGaussianposteriorforcoordinatesis



                             𝑞(𝑥𝑡−1  ∣  𝑥𝑡, 𝑥0)  =  𝒩(𝑥𝑡−1;      ̃𝜇𝑡(𝑥𝑡, 𝑥0),      ̃𝛽𝑥𝑡 𝐼 ) ,



with
                             ̃𝜇𝑡(𝑥𝑡, 𝑥0)  =   𝛽𝑥𝑡 √    ̄𝛼𝑥𝑡−1          𝛼𝑥𝑡 (1  −      ̄𝛼𝑥𝑡−1)
                                                1  −      ̄𝛼𝑥𝑡       𝑥0  +  √1  −      ̄𝛼𝑥𝑡               𝑥𝑡,

and

                                               𝛽𝑥𝑡   =  𝛽𝑥𝑡  1  −      ̄𝛼𝑥𝑡−1̃1  −      ̄𝛼𝑥𝑡     .



TargetDiffpredictsthedenoisedligand



                                            [    ̂𝑥0,     ̂𝑣0]  =  𝜙𝜃(𝑀𝑡, 𝑡, 𝑃),



andthenplugsthosepredictionsintotheclosed-formposteriors:



                    𝜇𝜃(𝑀𝑡, 𝑡, 𝑃)  =       ̃𝜇𝑡(𝑥𝑡,     ̂𝑥0),               𝑐𝜃(𝑀𝑡, 𝑡, 𝑃)  =      ̃𝑐𝑡(𝑣𝑡,     ̂𝑣0).




Fortheversionusedinthisthesis,thepositionbranchusesthedirect  𝑥0 parameter-

ization:

                                               ̂𝑥0  =  𝜙(𝑥)𝜃    (𝑥𝑡, 𝑣𝑡, 𝑡, 𝑃).




                                                           44

## Page 55

Thecoordinatetraininglossisthereforeadirectdenoised-coordinateregression:



                                                   𝑁𝐿
                                    𝐿pos  =     1𝑁𝐿∑   ∥    ̂𝑥0,𝑖  −  𝑥0,𝑖∥22 .
                                                   𝑖=1



A.4 TargetDiff: SE(3)-Equivariant Refinement


Thekeyequivariantupdatealternatesbetweenhidden-staterefinementandcoordi-

naterefinement:



                         ℎ(ℓ+1)𝑖              =  ℎ(ℓ)𝑖       +        ∑𝑓ℎ(𝑑 (ℓ)𝑖𝑗    , ℎ(ℓ)𝑖     , ℎ(ℓ)𝑗     , 𝑒𝑖𝑗 ) ,
                                             𝑗∈𝒱, 𝑗≠𝑖


         𝑥(ℓ+1)𝑖              =  𝑥(ℓ)𝑖       + 1lig(𝑖)       ∑(𝑥(ℓ)𝑖       −  𝑥(ℓ)𝑗     ) 𝑓𝑥(𝑑 (ℓ)𝑖𝑗    , ℎ(ℓ+1)𝑖            , ℎ(ℓ+1)𝑗            , 𝑒𝑖𝑗 ) ,
                                      𝑗∈𝒱, 𝑗≠𝑖

where

                                         𝑑 (ℓ)𝑖𝑗      =  ∥𝑥(ℓ)𝑖       −  𝑥(ℓ)𝑗     ∥2 .



ThisallowsTargetDifftoupdategeometryandnodefeatureswhilepreservingSE(3)-

equivariance.



A.5 PolyGen2D: Diffusion Schedule and Forward Process


ForPolyGen2D,letthecleanpolygonbe



                                                𝑥0  ∈  ℝ2𝑛


                                                     45

## Page 56

indenseform,orequivalently

                                               𝑥0  ∈  ℝ𝑛×2.



Thediffusionscheduleis



                                                                                               𝑡
       𝛽𝑡  =  𝛽start  +         𝑡𝑇  −  1  (𝛽end  −  𝛽start) ,               𝛼𝑡  =  1  −  𝛽𝑡,                    ̄𝛼𝑡  =∏𝛼𝑠,
                                                                                              𝑠=0


withposteriorvariance

                                           𝛽𝑡  =  𝛽𝑡 1  −      ̄𝛼𝑡−1̃1  −      ̄𝛼𝑡    .



TheforwardcorruptionusedbyPolyGen2Dis



                          𝑥𝑡  =  √   ̄𝛼𝑡  𝑥0  +  √1  −      ̄𝛼𝑡  𝜖,               𝜖  ∼  𝒩(0, 𝐼 ).



A.6 PolyGen2D: Prediction Target and Training Loss


PolyGen2Dsupportstwopredictiontargetsselectedbytheconfigurationfield



                               diffusion.prediction_target.




Indirect-clean-samplemode,thedenoiserpredicts



                                          ̂𝑢𝜃(𝑥𝑡, 𝑡)  =      ̂𝑥0,𝜃(𝑥𝑡, 𝑡),




                                                     46

## Page 57

andthelossis

                             ℒ𝑥0 (𝜃)  =  𝔼𝑥0, 𝑡, 𝜖 [∥    ̂𝑥0,𝜃(𝑥𝑡, 𝑡)  −  𝑥0∥22] .



Inepsilon-parameterizedmode,thedenoiserpredicts



                                            ̂𝑢𝜃(𝑥𝑡, 𝑡)  =      ̂𝜖𝜃(𝑥𝑡, 𝑡),



andthelossis

                               ℒ𝜖(𝜃)  =  𝔼𝑥0, 𝑡, 𝜖 [∥    ̂𝜖𝜃(𝑥𝑡, 𝑡)  −  𝜖∥22] .



Thetwoparameterizationsarerelatedby


                                       ̂𝑥0  =   𝑥𝑡  −  √1  −      ̄𝛼𝑡      ̂𝜖𝜃(𝑥𝑡, 𝑡),
                                                         √   ̄𝛼𝑡


andequivalently
                                     ̂𝜖𝜃(𝑥𝑡, 𝑡)  =   𝑥𝑡  −  √ ̄𝛼𝑡     ̂𝑥0,𝜃(𝑥𝑡, 𝑡).
                                                          √1  −      ̄𝛼𝑡


Thus,evenwhentrainedinepsilonmode,themodelcanalwaysbeconvertedtoan

impliedclean-sampleprediction.














                                                       47

## Page 58

A.7 PolyGen2D: Reverse Mean and Sampling Rule


ReversediffusioninPolyGen2Dalwayscomputesthemeanfromapredictedclean

sample. Theposteriormeanis


                   𝜇𝜃(𝑥𝑡, 𝑡)  =   𝛽𝑡√   ̄𝛼𝑡−1                 𝛼𝑡(1  −      ̄𝛼𝑡−1)
                                   1  −      ̄𝛼𝑡         ̂𝑥0,𝜃(𝑥𝑡, 𝑡)  +  √1  −      ̄𝛼𝑡              𝑥𝑡.



Ifthemodelwastrainedinepsilonmode,thesamplerfirstconverts



                                   ̂𝜖𝜃(𝑥𝑡, 𝑡)         ⟶             ̂𝑥0,𝜃(𝑥𝑡, 𝑡),



thenappliesthesameposterior-meanformula. Sobothparameterizationssharethe

sameancestralsamplerafterconversionto      ̂𝑥0,𝜃.


Withoutguidance,reversesamplinguses



                        𝑥𝑡−1  =  𝜇𝜃(𝑥𝑡, 𝑡)  +  √𝛽𝑡  𝑧,               𝑧  ∼  𝒩(0, 𝐼 ).̃



A.8 PolyGen2D: Denoiser Forms


MLP denoiser.         ForthedenseMLPdenoiser,theflattenedpolygonisconcatenated

withitstimeembedding:

                                        ℎ(0)  =  [𝑥𝑡; 𝜓(𝑡)].




                                                 48

## Page 59

Eachhiddenlayerapplies



                                 ℎ(ℓ)  =SiLU(𝑊 (ℓ)ℎ(ℓ−1)  +  𝑏(ℓ)) ,



andtheoutputlayerpredictstheconfigureddiffusiontarget:



                                      ̂𝑢𝜃(𝑥𝑡, 𝑡)  =  𝑊outℎ(𝐿)  +  𝑏out.




GCN denoiser.          FortheGCNdenoiser,nodefeaturesbeginas



                                          ℎ(0)𝑖        =  [𝑣𝑖; 𝜓(𝑡𝑔)],



where  𝑣𝑖   ∈   ℝ2 is the vertex coordinate and  𝑡𝑔 is the timestep of the polygon con-

tainingnode  𝑖.


Thecycleadjacencyis


                                         ⎧{{{
                                           1
                                           3 ,       𝑗  ∈  {𝑖  −  1, 𝑖, 𝑖  +  1},
                                 𝐴𝑖𝑗   = ⎨{{{⎩
                                           0,  otherwise.


Eachlayercomputes

                                      ̃ℎ(ℓ+1)  =  𝐴ℎ(ℓ)𝑊 (ℓ)  +  𝑏(ℓ),








                                                    49

## Page 60

thenappliesaresidualprojectionandnonlinearity:



                               ℎ(ℓ+1)  =SiLU(   ̃ℎ(ℓ+1)  +  𝑅(ℓ)ℎ(ℓ)) .




GAT denoiser.         FortheGATdenoiser,thenodefeaturesare



                                       ℎ(0)𝑖        =  [𝑣𝑖; 𝑝𝑖; 𝜓(𝑡𝑔)],



where  𝑝𝑖 isthecyclepositionalencoding



                  𝑝𝑖  =  [sin( 2𝜋𝑖𝑛     ) ,cos( 2𝜋𝑖𝑛     ) ,sin( 4𝜋𝑖𝑛     ) ,cos( 4𝜋𝑖𝑛     )] .




Forhead  𝑘,attentionscoresarecomputedas



                       𝑒(𝑘)𝑖𝑗      =LeakyReLU(⟨𝑎(𝑘)src ,     ̃ℎ(𝑘)𝑖      ⟩  +  ⟨𝑎(𝑘)trg  ,     ̃ℎ(𝑘)𝑗      ⟩) ,



withnormalizedattentionweights


                                   𝛼(𝑘)                   𝑖𝑗    )
                                     𝑖𝑗      =    exp(𝑒(𝑘)∑𝑢∈𝒩(𝑗)exp(𝑒(𝑘)
                                                                𝑢𝑗   ) .



ThesearchitecturesareusedwhencomparinghowMLP,GCN,andGATdenoisers

behaveonthepolygontask.





                                                   50

## Page 61

A.9 PolyGen2D: Guidance Models


Guidance regressors are trained on noisy polygons. The noisy input is produced

withthesameforwarddiffusionequation:



                                    𝑥𝑡  =  √  ̄𝛼𝑡  𝑥0  +  √1  −      ̄𝛼𝑡  𝜖.




Fortheclean-statesurrogateablation,thisreducestothe 𝑡  =  0case: Forcomparison,

theclean-onlysurrogateobjectiveis



                                     ℒcleanreg       =  (   ̂𝑦(𝑥0)  −  𝑦)2.




Forregression,thetargetisthescalarregularityscore,



                                             𝑦  =  𝑠(𝑥0),



andthelossis

                                     ℒreg  =  (   ̂𝑦(𝑥𝑡, 𝑡)  −  𝑦)2.














                                                  51

## Page 62

A.10 PolyGen2D: Guided Reverse Mean


Allguidancetermsactoncoordinates. Ifaguidancescorereturns  𝑔(𝑥𝑡, 𝑡),thenthe

reversemeanbecomes



                        𝜇guided𝜃           (𝑥𝑡, 𝑡)  =  𝜇𝜃(𝑥𝑡, 𝑡)  +       ̃𝛽𝑡  𝜆𝑡∇𝑥𝑡 𝑔(𝑥𝑡, 𝑡).




Forregressorguidance,

                                       𝑔reg(𝑥𝑡, 𝑡)  =     ̂𝑦(𝑥𝑡, 𝑡).



Foranalyticregularityguidance,



                                     𝑔regscore(𝑥𝑡, 𝑡)  =  𝑠(𝑥𝑡),



or,withatargetscore  𝑠⋆,



                               𝑔regscore(𝑥𝑡, 𝑡)  =  − (𝑠(𝑥𝑡)  −  𝑠⋆)2 .




Ifmultipleguidancetermsareactive,theyaresummed:



                                                     𝐾
                                   𝑔total(𝑥𝑡, 𝑡)  = ∑   𝑔𝑘(𝑥𝑡, 𝑡).
                                                    𝑘=1







                                                  52

## Page 63

A.11 PolyGen2D: Guidance Scheduling


Inscheduledguidance,

                                           𝜆𝑡  =  𝜆𝑤(𝑡)



where  𝜆istheoverallstrength,and  𝑤(𝑡)isthescheduleshape.


This is used to control whether guidance should be applied at all steps or concen-

tratedinlaterdenoisingstages.



A.12 Polygon Regularity Objective


Givenpolygonvertices  𝑣1, … , 𝑣𝑛  ∈  ℝ2,definecenteredcoordinates



                                                       𝑛
                                         ̃𝑣𝑖  =  𝑣𝑖  −  1𝑛∑𝑣𝑗 .
                                                      𝑗=1


LettheRMSradiusbe
                                               1  𝑛
                                    𝑟rms  =  √𝑛  ∑‖    ̃𝑣𝑖‖22  +  𝜀,
                                                 𝑖=1

andnormalizedcoordinates

                                              ̄𝑣𝑖  =         ̃𝑣𝑖𝑟rms .



Theedgelengthsare



                            𝑒𝑖  =  𝑣𝑖+1  −  𝑣𝑖,               ℓ𝑖  =  √‖𝑒𝑖‖22  +  𝜀.


                                                 53

## Page 64

Let  𝜃𝑖 denotetheinteriorangles,andletthecoefficientofvariationbe



                                  CV(𝑎1, … , 𝑎𝑛)  =         𝜎𝑎𝜇𝑎  +  𝜀 ,



where
                                𝑛                     1   𝑛
                     𝜇𝑎  =   1𝑛∑   𝑎𝑖,               𝜎𝑎  =  √𝑛∑(𝑎𝑖  −  𝜇𝑎)2  +  𝜀.
                               𝑖=1                       𝑖=1


Thedifferentiableregularityscoreisthen



CVedge  =CV(ℓ1, … , ℓ𝑛),    CVangle  =CV(𝜃1, … , 𝜃𝑛),    CVradius  =CV(‖   ̄𝑣1‖2, … , ‖    ̄𝑣𝑛‖2),



and

                   𝑠(𝑣)  =exp(−𝛼CVedge  −  𝛽CVangle  −  𝛾CVradius) .



Thisistheanalyticobjectiveusedintheregularity-guidanceexperiments.



A.13 PolyGen2D Pocket-Fit Objective


For pocket-conditioned experiments, PolyGen2D uses a differentiable geometric

fit score instead of an external docking procedure. Points are sampled along each

polygonedgeas

                                   𝑞𝑖,𝑓   =  (1  −  𝑓 ) 𝑣𝑖  +  𝑓  𝑣𝑖+1.







                                                 54

## Page 65

Here, 𝑞𝑖,𝑓 isasampledboundarypointbetweenconsecutivevertices 𝑣𝑖and 𝑣𝑖+1,and

thecollectionofallsuchsamplesisdenotedby  𝒬.


Toestimatehowmuchofthepolygonstaysinsidethepocket,thescorecomputes



                      inside_fraction  =     1|𝒬|   ∑sigmoid( 𝛿𝑞𝜏in ) .
                                               𝑞∈𝒬


Here,  𝛿𝑞isthesignedpocketmarginofsamplepoint  𝑞,sopositivevaluesmeanthe

pointisinsidethepocket,and  𝜏in controlshowsoftlythatinside/outsidetransition

ismeasured.


Thefullpocket-fitrewardisthen


        fit_score(𝑥)  =inside_fraction  −  𝑤outoutside_penalty

                         −  𝑤areaarea_ratio_penalty  −  𝑤clearclearance_penalty.


Here, the outside penalty measures how far boundary samples extend beyond the

pocket,thearea-ratiopenaltydiscouragespolygonswiththewrongoverallsizerel-

ativetothepocket, andtheclearancepenaltykeepsthepolygonfromhuggingthe

walltootightlyorfloatingtoolooselyinsidethepocket.














                                             55

## Page 66

Appendix B: PolyGen2D Output












































                Figure6.1: Trajectoryofdenoisingapolygon.








                                    56

## Page 67

Figure6.2: PolyGen2Dtrainingdata.



















                   57

## Page 68

Figure6.3: PolyGen2Dgenerateddata.




















                   58

## Page 69

Appendix C: TargetDiff Output










































                Figure6.4: MoleculesgeneratedbyTargetDiff.









                                     59

## Page 70

Figure6.5: MoremoleculesgeneratedbyTargetDiff.








                           60

## Page 71

Figure6.6: Moreoverlayedguidedandunguidedmolecules.


                              61

## Page 72

Appendix D: Scripts



Python Code


Thesesnippetsarecopieddirectlyfromtheimplementation,withonlysurrounding

unrelatedlinesomitted.



Sampler-side guidance update


   Listing1: Actualsampler-sideguidanceblockfrommolopt_score_model.py

######  guidance   #############

pos_model_mean = self.q_pos_posterior(x0=pos0_from_e, xt=ligand_pos,

    t=t, batch=batch_ligand)

pos_log_variance = extract(self.posterior_logvar, t, batch_ligand)

sigma = (0.5 * pos_log_variance).exp()

nonzero_mask = (1 - (t == 0).float())[batch_ligand].unsqueeze(-1)



guidance_active = guidance_model         is not  None   and  guidance_scale > 0

within_guidance_window = (

    (guidance_start_idx      is  None  or  i <= guidance_start_idx)

    and  (guidance_end_idx      is  None  or  i >= guidance_end_idx)

)

if guidance_active     and  within_guidance_window:

    with   torch.enable_grad():

                                         62

## Page 73

lig_pos_leaf = ligand_pos.detach().clone().requires_grad_(

True)

     score = guidance_model(

          ligand_pos=lig_pos_leaf,

          ligand_v=ligand_v,

          batch_ligand=batch_ligand,

          batch_protein=batch_protein,

          protein_pos=protein_pos,

     )

     score_mean = score.detach().mean().item()

     J = score.sum()

     grad = torch.autograd.grad(J, lig_pos_leaf)[0]



     grad_mean = scatter_mean(grad, batch_ligand, dim=0)

     grad = grad - grad_mean[batch_ligand]



var = sigma ** 2

if  guidance_scale_mode ==       "var":

     guidance_delta = guidance_scale * var * grad

elif  guidance_scale_mode ==       "sigma":

     guidance_delta = guidance_scale * sigma * grad

elif  guidance_scale_mode ==       "fixed":

     guidance_delta = guidance_scale * grad

else:

                                     63

## Page 74

raise  ValueError(f"Unknown      guidance_scale_mode      {

    guidance_scale_mode}")



     noise = torch.randn_like(ligand_pos)

     noise_term = nonzero_mask * (sigma * noise_scale) * noise

     ligand_pos_next = pos_model_mean + guidance_delta + noise_term

else:

     noise = torch.randn_like(ligand_pos)

     ligand_pos_next = pos_model_mean + nonzero_mask * (sigma *

    noise_scale) * noise

########   guidance   ##############




Default wrapper forward pass


 Listing2: ActualGuidedLigandContextWrapper.forwardcodefromguidance.py

def  forward(self, ligand_pos, ligand_v, batch_ligand, batch_protein,

    protein_pos=None):

     device = ligand_pos.device

     num_graphs = batch_ligand.max().item() + 1



     atomic_numbers = trans.get_atomic_number_from_index(

          ligand_v.detach().cpu(), mode=self.ligand_atom_mode

     )



                                          64

## Page 75

z_lig = torch.tensor(atomic_numbers, dtype=torch.long, device=

device)



use_provided_protein = (

     protein_pos    is  not  None

     and  batch_protein     is not  None

     and  protein_pos.size(0) == self.num_pocket_atoms * num_graphs

)

if  use_provided_protein:

     pocket_pos = protein_pos

     pocket_batch = batch_protein

else:

     pocket_pos = self.pocket_pos_centered.repeat(num_graphs, 1)

     pocket_batch = torch.arange(num_graphs, device=device).

repeat_interleave(self.num_pocket_atoms)



z_pocket = self.pocket_z.repeat(num_graphs).to(device)



pos = torch.cat([ligand_pos, pocket_pos], dim=0)

z = torch.cat([z_lig, z_pocket], dim=0)

batch = torch.cat([batch_ligand, pocket_batch], dim=0)

node_type = torch.cat([

     torch.ones(ligand_pos.size(0), dtype=torch.long, device=

device),

                                     65

## Page 76

torch.zeros(pocket_pos.size(0), dtype=torch.long, device=

    device),

     ])

     edge_index, edge_type = build_context_edges(

          pos=pos,

          node_type=node_type,

          batch=batch,

          r_ligand=self.r_ligand,

          r_cross=self.r_cross,

     )




     data = Data(

          pos=pos,

          z=z,

          batch=batch,

          node_type=node_type,

          edge_index=edge_index,

          edge_type=edge_type,

     )

     affinity = self.affinity_model(data)

     return  -affinity




Directed context-edge construction


                                          66

## Page 77

Listing3: Buildcontextedgescodefromguidance.py

def  build_context_edges(pos, node_type, batch=None, r_ligand=5.0,

    r_cross=6.0):

     if batch   is  None:

          batch = torch.zeros(pos.size(0), dtype=torch.long, device=pos

    .device)




     edge_src = []

     edge_dst = []

     edge_type = []



     for  b in  batch.unique():

          mask_b = batch == b

          idx = mask_b.nonzero(as_tuple=True)[0]

          if idx.numel() == 0:

               continue




          sub_pos = pos[idx]

          sub_type = node_type[idx]



          lig_local = (sub_type == LIGAND_NODE).nonzero(as_tuple=True)

    [0]

          poc_local = (sub_type == POCKET_NODE).nonzero(as_tuple=True)

    [0]

                                         67

## Page 78

if  lig_local.numel() > 0:

          lig_pos = sub_pos[lig_local]

          dist_ll = torch.cdist(lig_pos, lig_pos, p=2)

          keep_ll = dist_ll <= r_ligand

          keep_ll = keep_ll & ~torch.eye(lig_local.numel(), dtype=

torch.bool, device=pos.device)

          src_ll, dst_ll = keep_ll.nonzero(as_tuple=True)

          if  src_ll.numel() > 0:

               edge_src.append(idx[lig_local[src_ll]])

               edge_dst.append(idx[lig_local[dst_ll]])

               edge_type.append(torch.full((src_ll.numel(),),

EDGE_LIGAND_LIGAND, dtype=torch.long, device=pos.device))



     if  lig_local.numel() > 0      and  poc_local.numel() > 0:

          lig_pos = sub_pos[lig_local]

          poc_pos = sub_pos[poc_local]

          dist_pl = torch.cdist(poc_pos, lig_pos, p=2)

          keep_pl = dist_pl <= r_cross

          src_pl, dst_pl = keep_pl.nonzero(as_tuple=True)

          if  src_pl.numel() > 0:

               edge_src.append(idx[poc_local[src_pl]])

               edge_dst.append(idx[lig_local[dst_pl]])




                                     68

## Page 79

edge_type.append(torch.full((src_pl.numel(),),

    EDGE_POCKET_TO_LIGAND, dtype=torch.long, device=pos.device))



     if len(edge_src) == 0:

          return  (

               torch.empty(2, 0, dtype=torch.long, device=pos.device),

               torch.empty(0, dtype=torch.long, device=pos.device),

          )



     edge_index = torch.stack([torch.cat(edge_src), torch.cat(edge_dst

    )], dim=0)

     edge_type = torch.cat(edge_type, dim=0)

     return  edge_index, edge_type




PolyGen2D: Minimal Source Snippets


These snippets show the implementation of the training loss and guidance mean

shift.


   Listing4: CoreDDPMtraininglossin polygen2d/models/diffusion.py

t = torch.randint(0, self.config.n_steps, (b,), device=self.device,

    dtype=torch.long)

noise = torch.randn_like(x0)

x_t = self.q_sample(x0, t, noise, graph_batch=graph_batch)


                                         69

## Page 80

model_output = self.predict_model_output(x_t, t, graph_batch=

    graph_batch)



if self.config.prediction_target ==         "epsilon":

    loss = nn.functional.mse_loss(model_output, noise)

else:

    loss = nn.functional.mse_loss(model_output, x0)



  Listing5: Guidedreversemeanshiftin polygen2d/models/diffusion.py

model_output = self.predict_model_output(x_t, t, graph_batch=

    graph_batch)

x0_pred = self._model_output_to_x0(x_t, t, model_output, graph_batch=

    graph_batch)

model_mean = self.q_posterior_mean(x0_pred, x_t, t, graph_batch=

    graph_batch)



if guidance_grad     is not  None:

    grad = guidance_grad(x_t, t)        if  graph_batch    is None   else

        guidance_grad(x_t, t, graph_batch=graph_batch)

    model_mean = model_mean + posterior_var_t * grad











                                         70

## Page 81

References



 [1]  Jiaqi Guan, Wesley Wei Qian, Xingang Peng, Yufeng Su, Jian Peng, and

      Jianzhu Ma. 3d equivariant diffusion for target-aware molecule generation

      andaffinityprediction. In International Conference on Learning Representa-

      tions,2023.


 [2]  In Sub M. Han and Kelly M. Thayer. Reconnaissance of allostery via the

      restorationofnativep53dna-bindingdomaindynamicsinY220Cmutantp53

      tumorsuppressorprotein.  ACS Omega,9:19837–19847,2024. doi: 10.1021/

      acsomega.3c08509.


 [3]  O. Trott and A. J. Olson. Autodock vina: Improving the speed and accu-

      racyofdockingwithanewscoringfunction,efficientoptimization,andmul-

      tithreading.  Journal of Computational Chemistry,31(2):455–461,2010. doi:

      10.1002/jcc.21334.


 [4]  ArneSchneuing, CharlesHarris, YuanqiDu, KieranDidi, ArianJamasb, Ilia

      Igashov,WeitaoDu,CarlaGomes,TomL.Blundell,PietroLio,MaxWelling,

      Michael Bronstein, and Bruno Correia.  Structure-based drug design with

      equivariant diffusion models.    Nature  Computational  Science, 4:899–909,

      2024. doi: 10.1038/s43588-024-00737-x.


 [5]  SeulLee,JaehyeongJo,andSungJuHwang. Exploringchemicalspacewith




                                            71

## Page 82

score-based out-of-distribution generation. In Proceedings of the 40th Inter-

      national Conference on Machine Learning,2023.


 [6]  JonathanHo,AjayJain,andPieterAbbeel. Denoisingdiffusionprobabilistic

      models. In Advances in Neural Information Processing Systems,2020.


 [7]  AmiraAlakhdar,BarnabasPóczos,andNewellWashburn. Diffusionmodels

      indenovodrugdesign.  Journal of Chemical Information and Modeling,64:

      7238–7256,2024. doi: 10.1021/acs.jcim.4c01107.


 [8]  Haitao Lin, Yufei Huang, Odin Zhang, Siqi Ma, Meng Liu, Xuanjing Li,

      Lirong Wu, Jishui Wang, Tingjun Hou, and Stan Z. Li. DiffBP: generative

      diffusion of 3d molecules for target protein binding.  Chemical Science, 16:

      1417–1431,2025. doi: 10.1039/D4SC05894A.


 [9]  HaoQian,WenjingHuang,ShikuiTu,andLeiXu. KGDiff: towardsexplain-

      abletarget-awaremoleculegenerationwithknowledgeguidance. Briefings in

      Bioinformatics,25(1):bbad435,2024. doi: 10.1093/bib/bbad435.


[10]  TheodoreBeckSternlieb.Targetspecificdrugdesignwithdeepreinforcement

      learning. Master’sthesis,WesleyanUniversity,April2022.


[11]  Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones,

      Aidan N. Gomez, Łukasz Kaiser, and Illia Polosukhin. Attention is all you

      need. In Advances in Neural Information Processing Systems,2017.


[12]  Adam Paszke, Sam Gross, Francisco Massa, Adam Lerer, James Bradbury,

      Gregory Chanan, Trevor Killeen, Zeming Lin, Natalia Gimelshein, Luca

                                             72

## Page 83

Antiga,AlbanDesmaison,AndreasKöpf,EdwardYang,ZachDeVito,Martin

      Raison,AlykhanTejani,SasankChilamkurthy,BenoitSteiner,LuFang,Junjie

      Bai, and Soumith Chintala. Pytorch: An imperative style, high-performance

      deeplearninglibrary. In Advances in Neural Information Processing Systems

      32 (NeurIPS 2019),2019. doi: 10.48550/arXiv.1912.01703.


[13]  Prafulla Dhariwal and Alex Nichol. Diffusion models beat GANs on image

      synthesis. In Advances in Neural Information Processing Systems,2021.


[14]  JonathanHoandTimSalimans. Classifier-freediffusionguidance,2022.


[15]  G.Gkarmpounis,C.Vranis,N.Vretos,andP.Daras. Surveyongraphneural

      networks.  IEEE Access, 12:128816–128832, 2024. doi: 10.1109/ACCESS.

      2024.3456913.


[16]  Justin Gilmer, Samuel S. Schoenholz, Patrick F. Riley, Oriol Vinyals, and

      GeorgeE.Dahl. Neuralmessagepassingforquantumchemistry. In Proceed-

      ings of the 34th International Conference on Machine Learning,volume70of

      Proceedings of Machine Learning Research,pages1263–1272.PMLR,2017.


[17]  Chieh-Hsin Lai, Yang Song, Dongjun Kim, Yuki Mitsufuji, and Stefano Er-

      mon. Theprinciplesofdiffusionmodels,2025.


[18]  Tomer Weiss, Eduardo Mayo Yanes, Sabyasachi Chakraborty, Luca Cosmo,

      Alex M. Bronstein, and Renana Gershoni-Poranne. Guided diffusion for in-

      versemoleculardesign. Nature Computational Science,3(10):873–882,2023.

      doi: 10.1038/s43588-023-00532-0.

                                            73

## Page 84

[19]  ThomasN.KipfandMaxWelling. Semi-supervisedclassificationwithgraph

      convolutionalnetworks. In International Conference on Learning Represen-

      tations,2017.

















































                                            74
