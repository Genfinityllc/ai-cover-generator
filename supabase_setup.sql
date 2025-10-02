-- Supabase Setup for AI Cover Generator\n-- Run these commands in your Supabase SQL Editor\n\n-- Command 1:\nINSERT INTO storage.buckets (id, name, public)
        VALUES ('cover-images', 'cover-images', true)
        ON CONFLICT (id) DO NOTHING;\n\n-- Command 2:\nCREATE POLICY "Public read access for cover images" ON storage.objects
        FOR SELECT USING (bucket_id = 'cover-images');\n\n-- Command 3:\nCREATE POLICY "Authenticated users can upload cover images" ON storage.objects
        FOR INSERT WITH CHECK (bucket_id = 'cover-images' AND auth.role() = 'authenticated');\n\n-- Command 4:\nCREATE TABLE IF NOT EXISTS generated_images (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title TEXT NOT NULL,
            subtitle TEXT,
            client_id VARCHAR(100),
            image_url TEXT NOT NULL,
            image_size VARCHAR(20) NOT NULL DEFAULT '1800x900',
            generation_params JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );\n\n-- Command 5:\nCREATE TABLE IF NOT EXISTS client_logos (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            client_id VARCHAR(100) UNIQUE NOT NULL,
            logo_name VARCHAR(100) NOT NULL,
            lora_model_path TEXT,
            description TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );\n\n-- Command 6:\nINSERT INTO client_logos (client_id, logo_name, description) VALUES
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
        ON CONFLICT (client_id) DO NOTHING;\n\n