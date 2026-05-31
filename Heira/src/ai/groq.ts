import Groq from 'groq-sdk';
import { ENV } from '../config.js';

export const groq = new Groq({
    apiKey: ENV.GROQ_API_KEY,
});

// Using a fast and capable free model on Groq
export const MODEL = "llama-3.3-70b-versatile";
