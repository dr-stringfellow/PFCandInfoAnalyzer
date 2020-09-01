import FWCore.ParameterSet.Config as cms

process = cms.Process("PFCandInfo")

# initialize MessageLogger and output report
process.load("FWCore.MessageLogger.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

isMC = False

#load globaltag
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
process.GlobalTag.globaltag = "106X_mc2017_realistic_v7"

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring('file:root://xrootd-cms.infn.it///store/mc/RunIISummer19UL17MiniAOD/QCD_Pt-15to7000_TuneCP5_Flat2018_13TeV_pythia8/MINIAODSIM/FlatPU0to70_106X_mc2017_realistic_v6-v3/40000/FFEE2656-43CF-4247-8A06-8B04E8FF00F5.root'),
    #fileNames = cms.untracked.vstring('file:root://xrootd-cms.infn.it///store/mc/RunIISummer19UL17MiniAOD/QCD_Pt-15to7000_TuneCP5_Flat2018_13TeV_pythia8/MINIAODSIM/NoPU_106X_mc2017_realistic_v6-v3/40000/FDBFC4B3-F359-5B49-8F79-2075C6024381.root'),
    #fileNames = cms.untracked.vstring('file:/eos/user/f/fiemmi/JetMET/ntuplize/CMSSW_10_6_4/src/pickevents_PU_files_EXT40k/pickevents_1.root', 'file:/eos/user/f/fiemmi/JetMET/ntuplize/CMSSW_10_6_4/src/pickevents_PU_files_EXT40k/pickevents_2.root', 'file:/eos/user/f/fiemmi/JetMET/ntuplize/CMSSW_10_6_4/src/pickevents_PU_files_EXT40k/pickevents_3.root', 'file:/eos/user/f/fiemmi/JetMET/ntuplize/CMSSW_10_6_4/src/pickevents_PU_files_EXT40k/pickevents_4.root', 'file:/eos/user/f/fiemmi/JetMET/ntuplize/CMSSW_10_6_4/src/pickevents_PU_files_EXT40k/pickevents_5.root', 'file:/eos/user/f/fiemmi/JetMET/ntuplize/CMSSW_10_6_4/src/pickevents_PU_files_EXT40k/pickevents_6.root', 'file:/eos/user/f/fiemmi/JetMET/ntuplize/CMSSW_10_6_4/src/pickevents_PU_files_EXT40k/pickevents_7.root', 'file:/eos/user/f/fiemmi/JetMET/ntuplize/CMSSW_10_6_4/src/pickevents_PU_files_EXT40k/pickevents_8.root',),
    #fileNames = cms.untracked.vstring('file:root://xrootd-cms.infn.it///store/data/Run2017B/JetHT/MINIAOD/09Aug2019_UL2017-v1/270000/FC1A877A-9874-D143-B7D8-E16F1F1E2BB1.root'),
    
)

process.triggerSelection = cms.EDFilter("TriggerResultsFilter",
                                       triggerConditions = cms.vstring('HLT_PFHT1050_v*'),
                                       hltResults = cms.InputTag( "TriggerResults", "", "HLT" ),
                                       l1tResults = cms.InputTag( "" ),
                                       throw = cms.bool(False)
                                       )

"""
Update PUPPI to v15
"""

from RecoJets.JetProducers.ak4PFJets_cfi import ak4PFJets
process.ak4PuppiJets  = ak4PFJets.clone (src = 'puppi', doAreaFastjet = True, jetPtMin = 2.)

from PhysicsTools.PatAlgos.tools.jetTools import addJetCollection
addJetCollection(process, labelName = 'Puppi', jetSource = cms.InputTag('ak4PuppiJets'), algo = 'AK', rParam=0.4, genJetCollection=cms.InputTag('slimmedGenJets'), jetCorrections = ('AK4PFPuppi', ['L1FastJet', 'L2Relative', 'L3Absolute','L2L3Residual'], 'None'), pfCandidates = cms.InputTag('packedPFCandidates'), pvSource = cms.InputTag('offlineSlimmedPrimaryVertices'), svSource = cms.InputTag('slimmedSecondaryVertices'), muSource =cms.InputTag( 'slimmedMuons'), elSource = cms.InputTag('slimmedElectrons'), genParticles= cms.InputTag('prunedGenParticles'), getJetMCFlavour=isMC)                                                                                                        

process.patJetsPuppi.addGenPartonMatch = cms.bool(isMC)                                                                                                          
process.patJetsPuppi.addGenJetMatch = cms.bool(isMC)

from CommonTools.PileupAlgos.customizePuppiTune_cff import UpdatePuppiTuneV15
UpdatePuppiTuneV15(process, isMC)

process.GetPFInfo = cms.EDAnalyzer('PFCandInfoAnalyzer',
                                   vertices  = cms.InputTag("offlineSlimmedPrimaryVertices"),
                                   PUinfo  = cms.InputTag("slimmedAddPileupInfo"),
                                   AK4PUPPIJets  = cms.InputTag("slimmedJetsPuppi"),
                                   #AK4PUPPIv15Jets  = cms.InputTag("patJetsPuppi"),
                                   AK4CHSJets  = cms.InputTag("slimmedJets"),
                                   AK4GenJets = cms.InputTag("slimmedGenJets"),
                                   PFCands  = cms.InputTag("packedPFCandidates"),
                                   muons = cms.InputTag("slimmedMuons"),
                                   electrons = cms.InputTag("slimmedElectrons"),
                                   missingEt = cms.InputTag("slimmedMETs"),
                                   PUPPImissingEt = cms.InputTag("slimmedMETsPuppi"),
                                   triggerNames = cms.vstring (
                                       "HLT_PFHT1050_v",
                                       "HLT_PFJet500_v",
                                       "HLT_PFJet550_v",
                                   ),
                                   triggerResults = cms.InputTag('TriggerResults','','HLT'),
                                   runOnMC = cms.untracked.bool(isMC)
)

process.TFileService = cms.Service("TFileService",
                                       #fileName = cms.string('flatTree_QCD_Pt-15to7000_TuneCP5_Flat2018_13TeV_pythia8_ext.root')
                                       #fileName = cms.string('flatTree_QCD_Pt-15to7000_TuneCP5_Flat2018_13TeV_pythia8_PU_EXT.root')
                                       #fileName = cms.string('flatTree_QCD_Pt-15to7000_TuneCP5_Flat2018_13TeV_pythia8_training_noPU_EXT40k.root')
                                       #fileName = cms.string('flatTree_QCD_Pt-15to7000_TuneCP5_Flat2018_13TeV_pythia8_training_PU_EXT40k.root')
                                       #fileName = cms.string('flatTree_JetHT_Run2017B_HLTPFHT1050.root')
                                       fileName = cms.string('try.root')
                                   )

process.p = cms.Path(process.puppiSequence*process.GetPFInfo)

#print process.dumpPython() 
