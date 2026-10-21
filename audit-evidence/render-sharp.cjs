const fs=require('fs'),path=require('path'),sharp=require('sharp');
(async()=>{for(const name of fs.readdirSync('audit-evidence').filter(n=>/^(before|after)-.*\.svg$/.test(n)))await sharp(path.join('audit-evidence',name)).png().toFile(path.join('audit-evidence',name.replace('.svg','.png')));})();
