#!/usr/bin/env python3
"""
Setup Supabase Storage for AI Cover Generator
Creates necessary storage buckets and database tables
"""

def create_storage_sql():
    """Generate SQL to create storage bucket and tables"""
    
    sql_commands = [
        # Create storage bucket for cover images
        """
        INSERT INTO storage.buckets (id, name, public)
        VALUES ('cover-images', 'cover-images', true)
        ON CONFLICT (id) DO NOTHING;
        """,
        
        # Create policy to allow public read access to cover images
        """
        CREATE POLICY "Public read access for cover images" ON storage.objects
        FOR SELECT USING (bucket_id = 'cover-images');
        """,
        
        # Create policy to allow authenticated users to upload cover images
        """
        CREATE POLICY "Authenticated users can upload cover images" ON storage.objects
        FOR INSERT WITH CHECK (bucket_id = 'cover-images' AND auth.role() = 'authenticated');
        """,
        
        # Create table for generated images metadata
        """
        CREATE TABLE IF NOT EXISTS generated_images (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title TEXT NOT NULL,
            subtitle TEXT,
            client_id VARCHAR(100),
            image_url TEXT NOT NULL,
            image_size VARCHAR(20) NOT NULL DEFAULT '1800x900',
            generation_params JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Create table for client/logo mappings
        """
        CREATE TABLE IF NOT EXISTS client_logos (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            client_id VARCHAR(100) UNIQUE NOT NULL,
            logo_name VARCHAR(100) NOT NULL,
            lora_model_path TEXT,
            description TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Insert your client mappings
        """
        INSERT INTO client_logos (client_id, logo_name, description) VALUES
        ('xdc', 'xdc_network', 'XDC Network - Enterprise blockchain'),
        ('xdc_network', 'xdc_network', 'XDC Network - Main logo'),
        ('xdc_logo', 'xdc_logo', 'XDC Network - Alternative logo'),
        ('hedera', 'hedera', 'Hedera Hashgraph - Main network'),
        ('hedera_foundation', 'hedera_foundation', 'Hedera Foundation'),
        ('hbar', 'hbar', 'HBAR - Hedera native token'),
        ('hashpack', 'hashpack', 'HashPack - Hedera wallet'),
        ('hashpack_color', 'hashpack_color', 'HashPack - Color version'),
        ('constellation', 'constellation', 'Constellation - DAG network'),
        ('dag', 'constellation', 'Constellation - DAG network'),
        ('constellation_alt', 'constellation_alt', 'Constellation - Alternative'),
        ('algorand', 'algorand', 'Algorand - Blockchain platform'),
        ('algo', 'algorand', 'Algorand - Short name'),
        ('tha', 'tha', 'THA - Blockchain services'),
        ('tha_color', 'tha_color', 'THA - Color version'),
        ('genfinity', 'genfinity', 'Genfinity - Crypto media'),
        ('gen', 'genfinity', 'Genfinity - Short name'),
        ('genfinity_black', 'genfinity_black', 'Genfinity - Black version')
        ON CONFLICT (client_id) DO NOTHING;
        """
    ]
    
    return sql_commands

def main():
    """Setup Supabase storage and database"""
    
    print("🔧 Supabase Storage Setup for AI Cover Generator")
    print("=" * 60)
    
    # Generate SQL commands
    sql_commands = create_storage_sql()
    
    print("📝 SQL Commands to execute in Supabase:")
    print("1. Go to your Supabase dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Run these commands:")
    print()
    
    for i, sql in enumerate(sql_commands, 1):
        print(f"-- Command {i}:")
        print(sql.strip())
        print()
    
    # Save to file
    with open("supabase_setup.sql", "w") as f:
        f.write("-- Supabase Setup for AI Cover Generator\\n")
        f.write("-- Run these commands in your Supabase SQL Editor\\n\\n")
        
        for i, sql in enumerate(sql_commands, 1):
            f.write(f"-- Command {i}:\\n")
            f.write(sql.strip() + "\\n\\n")
    
    print("💾 SQL commands saved to: supabase_setup.sql")
    print()
    print("🚀 Next steps:")
    print("1. Copy the SQL commands above")
    print("2. Go to https://supabase.com/dashboard/projects")
    print("3. Select your 'crypto-news-curator' project")
    print("4. Go to SQL Editor")
    print("5. Paste and run each command")
    print("6. Come back here when done!")
    
    return 0

if __name__ == "__main__":
    exit(main())