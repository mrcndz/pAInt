-- Add session_uuid column to chat_sessions table for public identification
-- This migration adds the session_uuid field needed for the conversation persistence feature

ALTER TABLE chat_sessions 
ADD COLUMN session_uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Create index for session_uuid lookups
CREATE INDEX idx_chat_sessions_session_uuid ON chat_sessions(session_uuid);

-- Create trigger for updated_at column
CREATE TRIGGER update_chat_sessions_updated_at 
    BEFORE UPDATE ON chat_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Update existing records to have session_uuid
UPDATE chat_sessions SET session_uuid = uuid_generate_v4() WHERE session_uuid IS NULL;

-- Make session_uuid NOT NULL after updating existing records
ALTER TABLE chat_sessions ALTER COLUMN session_uuid SET NOT NULL;