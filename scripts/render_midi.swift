import AVFoundation
import Foundation

guard CommandLine.arguments.count == 3 else {
  fatalError("usage: render_midi.swift input.mid output.wav")
}
let midiURL = URL(fileURLWithPath: CommandLine.arguments[1])
let outputURL = URL(fileURLWithPath: CommandLine.arguments[2])
let bankURL = URL(fileURLWithPath: "/System/Library/Components/CoreAudio.component/Contents/Resources/gs_instruments.dls")

let engine = AVAudioEngine()
let piano = AVAudioUnitSampler()
let room = AVAudioUnitReverb()
engine.attach(piano); engine.attach(room)
let format = AVAudioFormat(standardFormatWithSampleRate: 44_100, channels: 2)!
room.loadFactoryPreset(.mediumRoom)
room.wetDryMix = 12
engine.connect(piano, to: room, format: format)
engine.connect(room, to: engine.mainMixerNode, format: format)
try piano.loadSoundBankInstrument(at: bankURL, program: 0, bankMSB: UInt8(kAUSampler_DefaultMelodicBankMSB), bankLSB: UInt8(kAUSampler_DefaultBankLSB))

let sequencer = AVAudioSequencer(audioEngine: engine)
try sequencer.load(from: midiURL, options: [])
let musicTracks = sequencer.tracks
if musicTracks.count >= 2 {
  musicTracks[0].destinationAudioUnit = piano
  musicTracks[1].destinationAudioUnit = piano
}

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
