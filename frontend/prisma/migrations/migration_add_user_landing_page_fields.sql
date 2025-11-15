-- AddUserLandingPageFields Migration
-- This migration adds fields from the landing page form to the User model

-- Add new columns to users table
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "school" TEXT;
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "focusArea" TEXT;
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "entryYear" INTEGER;
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "apCredits" TEXT[] DEFAULT ARRAY[]::TEXT[];
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "additionalDetails" TEXT;

-- Note: major and graduationYear already exist in the schema
