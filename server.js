const express = require('express');
const fs = require('fs').promises;
const path = require('path');
const { exec } = require('child_process');

const app = express();
const port = 3000;

app.use(express.static('.'));
app.use(express.json());

app.use('/output', express.static(path.join(__dirname, 'output')));

app.post('/submit', async (req, res) => {
    try {
        const jsonData = JSON.stringify(req.body, null, 2);
        await fs.writeFile('input.json', jsonData);

        // Invoke Python script
        exec('python3 ./scripts/graph.py', async (error, stdout, stderr) => {
            if (error) {
                console.error(`Error: ${error.message}`);
                return res.status(500).send('Error processing data');
            }
            if (stderr) {
                console.error(`stderr: ${stderr}`);
                return res.status(500).send('Error processing data');
            }
            console.log(`Python script output: ${stdout}`);

            // // Send the JSON file
            // //res.download('input.json');
            // try {
            //     const result = JSON.parse(stdout);
            //     res.json({ pdf_url: result.pdf_url });
            // } catch (e) {
            //     res.status(500).json({ error: 'Invalid output from Python script' + stdout });
            // }
            // Read image files from the output folder
            const outputFolder = path.join(__dirname, 'output');
            const files = await fs.readdir(outputFolder);
            const imageFiles = files.filter(file => file.match(/\.(jpg|jpeg|png|gif)$/i));

            // Generate URLs for each image
            const imageUrls = imageFiles.map(file => `/output/${file}`);

            res.json({ imageUrls: imageUrls });
        });
    } catch (err) {
        console.error(err);
        res.status(500).send('Server error');
    }
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});

// app.get('/generate_pdf', (req, res) => {
//     res.json({ pdf_url: '/output/output.pdf' });
// });
