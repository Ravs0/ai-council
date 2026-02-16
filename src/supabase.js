
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_KEY

let supabase = null

if (supabaseUrl && supabaseKey) {
    try {
        supabase = createClient(supabaseUrl, supabaseKey)
        console.log("Supabase client initialized.")
    } catch (e) {
        console.error("Failed to initialize Supabase client:", e)
    }
} else {
    console.warn("Supabase credentials missing. Check .env file.")
}

export { supabase }
