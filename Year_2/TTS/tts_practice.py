from google.cloud import texttospeech

def synthesize_with_us_casual_k(text, output_file="output_us_casual_k.mp3"):
    client = texttospeech.TextToSpeechClient()

    voice_params = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="am-ET-Standard-B",
        ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    synthesis_input = texttospeech.SynthesisInput(text=text)

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice_params, audio_config=audio_config
    )

    with open(output_file, "wb") as out:
        out.write(response.audio_content)
    print(f"Saved synthesized speech to {output_file}")

if __name__ == "__main__":
    synthesize_with_us_casual_k("This is a Reddit story about someone who...")
