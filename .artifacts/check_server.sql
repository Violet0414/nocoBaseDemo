SELECT id, title FROM "desktopRoutes" WHERE id IN (396915888357376, 396915913523200, 396915917717504);
SELECT setting_value AS site_title FROM "systemSettings" WHERE key='systemSettings.title' LIMIT 1;
SELECT enabled FROM "applicationPlugins" WHERE name='ai';
SELECT uid, options::text LIKE '%"mode":"custom"%' AS is_custom FROM "flowModels" WHERE uid IN ('gsunigj6u9n','vdx0vcdwurk','llxve6isxx6','73fclpvn4nr');
SELECT options::text LIKE '%?embed=1%' AS has_embed FROM "flowModels" WHERE uid IN ('s96hi0xk166','ykhawbr91vm','6nia4y84u97');
