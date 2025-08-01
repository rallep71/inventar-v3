-- Add missing fields to items table
-- Run: mysql -u root -p inventar_v3 < add_missing_fields.sql

-- Check and add purchase_price if not exists
ALTER TABLE items ADD COLUMN IF NOT EXISTS purchase_price DECIMAL(10,2) DEFAULT NULL;

-- Check and add room if not exists  
ALTER TABLE items ADD COLUMN IF NOT EXISTS room VARCHAR(100) DEFAULT NULL;

-- Check and add shelf if not exists
ALTER TABLE items ADD COLUMN IF NOT EXISTS shelf VARCHAR(50) DEFAULT NULL;

-- Check and add compartment if not exists
ALTER TABLE items ADD COLUMN IF NOT EXISTS compartment VARCHAR(50) DEFAULT NULL;

-- Check and add model if not exists
ALTER TABLE items ADD COLUMN IF NOT EXISTS model VARCHAR(100) DEFAULT NULL;

-- Check and add description if not exists (maps to notes in model)
-- Note: The model uses 'notes' but we might have 'description' in DB
ALTER TABLE items ADD COLUMN IF NOT EXISTS notes TEXT DEFAULT NULL;

-- Check and add serial_number if not exists
ALTER TABLE items ADD COLUMN IF NOT EXISTS serial_number VARCHAR(100) DEFAULT NULL;

-- Check and add condition if not exists
ALTER TABLE items ADD COLUMN IF NOT EXISTS `condition` VARCHAR(50) DEFAULT 'Gut';

-- Check and add team_id if not exists
ALTER TABLE items ADD COLUMN IF NOT EXISTS team_id INT DEFAULT NULL;
ALTER TABLE items ADD CONSTRAINT IF NOT EXISTS fk_items_team 
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL;

-- Show final structure
DESCRIBE items;
