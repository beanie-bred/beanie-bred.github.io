import AVFoundation
import Foundation

guard CommandLine.arguments.count == 3 else {
  fatalError("usage: render_midi.swift input.mid output.wav")
}
let midiURL = URL(fileURLWithPath: CommandLine.arguments[1])
let outputURL = URL(fileURLWithPath: CommandLine.arguments[2])
let bankURL = URL(fileURLWithPath: "/System/Library/Components/CoreAudio.component/Contents/Resources/gs_instruments.dls")
let sampledPianoURL = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
  .appendingPathComponent("audio/instruments/SalamanderGrandPianoV3_44.1khz16bit/SalamanderGrandPianoV3.sfz")

let engine = AVAudioEngine()
let piano = AVAudioUnitSampler()
let bass = AVAudioUnitSampler()
let drums = AVAudioUnitSampler()
let ensemble = AVAudioMixerNode()
let room = AVAudioUnitReverb()
let mastering = AVAudioUnitEQ(numberOfBands: 0)
engine.attach(piano); engine.attach(bass); engine.attach(drums); engine.attach(ensemble); engine.attach(room); engine.attach(mastering)
let format = AVAudioFormat(standardFormatWithSampleRate: 44_100, channels: 2)!
room.loadFactoryPreset(.mediumRoom)
room.wetDryMix = 14
piano.masterGain = 4
bass.masterGain = 0
drums.masterGain = -6
mastering.globalGain = 12
engine.connect(piano, to: ensemble, fromBus: 0, toBus: 0, format: format)
engine.connect(bass, to: ensemble, fromBus: 0, toBus: 1, format: format)
engine.connect(drums, to: ensemble, fromBus: 0, toBus: 2, format: format)
engine.connect(ensemble, to: room, format: format)
engine.connect(room, to: mastering, format: format)
engine.connect(mastering, to: engine.mainMixerNode, format: format)
if FileManager.default.fileExists(atPath: sampledPianoURL.path) {
  try piano.loadInstrument(at: sampledPianoURL)
  print("Using sampled Yamaha C5: \(sampledPianoURL.path)")
} else {
  try piano.loadSoundBankInstrument(at: bankURL, program: 0, bankMSB: UInt8(kAUSampler_DefaultMelodicBankMSB), bankLSB: UInt8(kAUSampler_DefaultBankLSB))
  print("Yamaha samples missing; using macOS acoustic grand fallback")
}
try bass.loadSoundBankInstrument(at: bankURL, program: 32, bankMSB: UInt8(kAUSampler_DefaultMelodicBankMSB), bankLSB: UInt8(kAUSampler_DefaultBankLSB))
try drums.loadSoundBankInstrument(at: bankURL, program: 0, bankMSB: UInt8(kAUSampler_DefaultPercussionBankMSB), bankLSB: UInt8(kAUSampler_DefaultBankLSB))

let sequencer = AVAudioSequencer(audioEngine: engine)
try sequencer.load(from: midiURL, options: [])
let musicTracks = sequencer.tracks
if musicTracks.count >= 2 {
  musicTracks[0].destinationAudioUnit = piano
  musicTracks[1].destinationAudioUnit = piano
}
if musicTracks.count >= 3 { musicTracks[2].destinationAudioUnit = bass }
if musicTracks.count >= 4 { musicTracks[3].destinationAudioUnit = drums }

try? FileManager.default.removeItem(at: outputURL)
let file = try AVAudioFile(forWriting: outputURL, settings: format.settings)
try engine.enableManualRenderingMode(.offline, format: format, maximumFrameCount: 4096)
try engine.start()
sequencer.currentPositionInBeats = 0
try sequencer.start()

let seconds = musicTracks.map { $0.lengthInSeconds }.max() ?? 1
let totalFrames = AVAudioFramePosition(seconds * format.sampleRate)
let buffer = AVAudioPCMBuffer(pcmFormat: engine.manualRenderingFormat, frameCapacity: 4096)!
while engine.manualRenderingSampleTime < totalFrames {
  let remaining = totalFrames - engine.manualRenderingSampleTime
  let frames = min(buffer.frameCapacity, AVAudioFrameCount(remaining))
  switch try engine.renderOffline(frames, to: buffer) {
  case .success: try file.write(from: buffer)
  case .cannotDoInCurrentContext: continue
  case .insufficientDataFromInputNode: continue
  case .error: fatalError("offline rendering failed")
  @unknown default: fatalError("unknown rendering status")
  }
}
sequencer.stop(); engine.stop()
print(outputURL.path)
