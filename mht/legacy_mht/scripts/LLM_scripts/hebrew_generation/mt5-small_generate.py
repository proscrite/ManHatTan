from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

def main():
    model_name="Norod78/distilgpt2-base-pretrained-he"

    prompt_text = "שלום, קוראים לי"
    generated_max_length = 192

    print("Loading model...")
    model =  AutoModelForCausalLM.from_pretrained(model_name)
    print('Loading Tokenizer...')
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    text_generator = pipeline(task="text-generation", model=model, tokenizer=tokenizer)

    print("Generating text...")
    result = text_generator(prompt_text, num_return_sequences=1, batch_size=1, do_sample=True, top_k=40, top_p=0.92, temperature = 1, repetition_penalty=5.0, max_length = generated_max_length)

    print("result = " + str(result))

if __name__ == '__main__':
    main()
