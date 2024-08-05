from flask import Flask, render_template, request
import aiohttp
import asyncio
import requests
import re
import subprocess
import base64
from bs4 import BeautifulSoup
import time
import aiofiles
from urllib.parse import urljoin


app = Flask(__name__)

subdomains = []
@app.route('/')
def home():
    for subdomain in subdomains_robots:
        input_string = subdomain
        pattern = r'https://[^\s]+'
        # Find the URL
        match = re.search(pattern, input_string)
        if match:
            url = match.group(0)
            # Remove the 'http://' prefix
            output = url.replace('https://', '')
            # Check if the URL ends with '/'
            if output.endswith('/'):
                subdomains.append(output[:-1])

    return render_template('index.html')

subdomains_robots = []

@app.route('/robots', methods=['POST'])
async def robots():
    ip_address = request.form['ip']
    subdomains_robot = []

    async def fetch_url(session, url):
        try:
            async with session.get(url, timeout=10) as response:
                response_number = response.status
                content = await response.text()
                length = len(content)
                return f"Status: {response_number} Length: {length} {url}"
        except Exception as e:
            return f"Error fetching {url}: {e}"

    async def process_robots():
        try:
            async with aiohttp.ClientSession() as session:
                robots_url = f'https://{ip_address}/robots.txt'
                async with session.get(robots_url) as response:
                    robots_content = await response.text()
                
                disallowed_paths = [
                    line.split(': /')[1].strip() 
                    for line in robots_content.split('\n') 
                    if line.startswith('Disallow')
                ]

                tasks = [
                    fetch_url(session, f'https://{ip_address}/{path}') 
                    for path in disallowed_paths
                ]
                results = await asyncio.gather(*tasks)
                subdomains_robot.extend(results)

        except Exception as e:
            subdomains_robot.append(f"Error fetching robots.txt: {e}")

    await process_robots()
    
    subdomains_robot.sort()
    subdomains_robots.extend(subdomains_robot)
    
    return render_template('robots_result.html', data=subdomains_robots)

@app.route('/lookup', methods=['POST'])
def lookup():
    ip_address = request.form['ip']
    response = requests.get(f'http://ip-api.com/json/{ip_address}')
    data = response.json()
    return render_template('result.html', data=data)

async def fetch(session, url):
    try:
        async with session.get(url) as response:
            status = response.status
            length = len(await response.text())
            result = f"Status: {status} Length: {length} {url}"
            with open('output_file.txt', 'a') as file:
                file.write(result + '\n')
            return result
    except aiohttp.ClientError as e:
        result = f"Error fetching {url}: {e}"
        with open('output_file.txt', 'a') as file:
            file.write(result + '\n')
        return result

async def worker(queue, session, results):
    while True:
        subdomain = await queue.get()
        if subdomain is None:
            break
        url = subdomain
        result = await fetch(session, url)
        results.append(result)
        queue.task_done()

@app.route('/subdomains_finder', methods=['POST'])
def subdomain_finder():
    ip_address = request.form['ip']
    results = []
    queue = asyncio.Queue()
    num_workers = 100  # Adjust the number of workers based on your needs

    def read_subdomains_in_chunks(file_path, chunk_size=100):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            chunk = []
            for line in file:
                chunk.append(line.strip())
                if len(chunk) >= chunk_size:
                    yield chunk
                    chunk = []
            if chunk:
                yield chunk

    async def process_subdomains():
        async with aiohttp.ClientSession() as session:
            tasks = []
            for chunk in read_subdomains_in_chunks('subdomains.txt'):
                for subdomain in chunk:
                    url = f'https://{ip_address}/{subdomain}'
                    queue.put_nowait(url)
                
            for _ in range(num_workers):
                task = asyncio.create_task(worker(queue, session, results))
                tasks.append(task)
            
            await queue.join()
            for _ in range(num_workers):
                queue.put_nowait(None)
            await asyncio.gather(*tasks)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_subdomains())
    return render_template('subdomains_result.html', results=results)

@app.route('/robots_subdomain_finder', methods=['POST'])
async def robots_subdomain_finder():
    results = []

    async def fetch(session, url):
        try:
            async with session.get(url, timeout=10) as response:
                status = response.status
                content = await response.text()
                length = len(content)
                result = f"Status: {status} Length: {length} {url}"
                results.append(result)
                with open('output_file.txt', 'a') as file:
                    file.write(result + '\n')
                return result
        except aiohttp.ClientError as e:
            result = f"Error fetching {url}: {e}"
            results.append(result)
            with open('output_file.txt', 'a') as file:
                file.write(result + '\n')
            return result

    async def worker(queue, session):
        while True:
            url = await queue.get()
            if url is None:
                break
            await fetch(session, url)
            queue.task_done()

    async def process_subdomains(subdomains, subdirectories):
        queue = asyncio.Queue()
        num_workers = 100

        async with aiohttp.ClientSession() as session:
            for subdomain in subdomains:
                for subdirectory in subdirectories:
                    url = f'https://{subdomain}/{subdirectory}'
                    await queue.put(url)

            workers = [asyncio.create_task(worker(queue, session)) for _ in range(num_workers)]

            await queue.join()

            for _ in range(num_workers):
                await queue.put(None)

            await asyncio.gather(*workers)

    # Read subdirectories from subdomains.txt
    with open('subdomains.txt', 'r') as file:
        subdirectories = [line.strip() for line in file if line.strip()]

    await process_subdomains(subdomains, subdirectories)
    
    return render_template('subdomains_result.html', results=results)



@app.route('/output', methods=['GET', 'POST'])
def output():
    subprocess.Popen('sort output_file.txt > sorted_output.txt', shell=True).wait()
    status_code_filter = request.form.get('status_code')
    url_filter = request.form.get('url')

    try:
        with open('sorted_output.txt', 'r') as file:
            lines = file.readlines()

        # Parse the lines
        parsed_lines = []
        for line in lines:
            match = re.match(r'Status: (\d+) Length: (\d+) (.+)', line)
            if match:
                status_code = int(match.group(1))
                length = int(match.group(2))
                url = match.group(3)
                parsed_lines.append((status_code, length, url))

        # Apply filters
        if status_code_filter:
            parsed_lines = [line for line in parsed_lines if line[0] == int(status_code_filter)]
        if url_filter:
            parsed_lines = [line for line in parsed_lines if url_filter in line[2]]

        sorted_lines = sorted(parsed_lines, key=lambda x: x[0])

    except FileNotFoundError:
        sorted_lines = [("Output file not found.",)]

    return render_template('output.html', sorted_lines=sorted_lines, status_code_filter=status_code_filter, url_filter=url_filter)

@app.route('/CTF_Finder', methods=['POST'])
async def ctf_finder():
    string_input = request.form['string']
    ip_address = request.form['ip']
    ctf_robots_subdirectory = []

    async def fetch_url(session, url):
        try:
            async with session.get(url, timeout=10) as response:
                response_number = response.status
                content = await response.text()
                if response_number == 200:
                    if re.search(re.escape(string_input), content):
                        ctf_robots_subdirectory.append(f"Found in {url} as Plain Text")

                    string_bytes = string_input.encode('utf-8')
                    base64_bytes = base64.b64encode(string_bytes)
                    base64_string = base64_bytes.decode('utf-8')

                    if re.search(re.escape(base64_string), content):
                        ctf_robots_subdirectory.append(f"Found in {url} as Base64 Text")

                return f"Status: {response_number} Length: {len(content)} {url}"
        except Exception as e:
            return f"Error fetching {url}: {e}"

    async def process_robots():
        try:
            async with aiohttp.ClientSession() as session:
                robots_url = f'https://{ip_address}/robots.txt'
                async with session.get(robots_url) as response:
                    robots_content = await response.text()

                disallowed_paths = [
                    line.split(': /')[1].strip()
                    for line in robots_content.split('\n')
                    if line.startswith('Disallow')
                ]

                tasks = [
                    fetch_url(session, f'https://{ip_address}/{path}')
                    for path in disallowed_paths
                ]
                await asyncio.gather(*tasks)

        except Exception as e:
            ctf_robots_subdirectory.append(f"Error fetching robots.txt: {e}")

    await process_robots()

    return render_template('robots_result.html', data=ctf_robots_subdirectory)

@app.route('/nmap_scanner', methods=['GET', 'POST'])
def nmap_scanner():
    if request.method == 'POST':
        ip_address = request.form['ip']
        scan_type = request.form['scan_type']
        
        # Define the nmap command based on the selected scan type
        if scan_type == 'Ping Scan':
            command = f'nmap {ip_address} -sn'
        elif scan_type == 'Regular Scan':
            command = f'nmap {ip_address} '
        elif scan_type == 'Quick traceroute':
            command = f'nmap {ip_address} -sn --traceroute'
        elif scan_type == 'Quick scan':
            command = f'nmap {ip_address} -T4 -F '
        elif scan_type == 'Quick scan plus':
            command = f'sudo nmap {ip_address} -sV -T4 -O -F --version-light'
        elif scan_type == 'Intense scan':
            command = f'nmap {ip_address} -T4 -A -v '
        elif scan_type == 'Intense scan, all TCP ports':
            command = f'nmap {ip_address} -p 1-65535 -T4 -A -v '
        elif scan_type == 'Intense scan plus UDP':
            command = f'nmap {ip_address} -sS -sU -T4 -A -v '
        elif scan_type == 'Intense scan, no ping':
            command = f'nmap {ip_address} -T4 -A -v -Pn '
        elif scan_type == 'Slow comprehensive scan':
            command = f'nmap {ip_address} -sS -sU -T4 -A -v -PE -PP -PS80,443 -PA3389 -PU40125 -PY -g 53 --script "default or (discovery and safe)" '                                  
        else:
            command = f'nmap {ip_address} -sn'
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout

        with open('nmap_output.txt', 'w') as file:
            file.write(output)

        return render_template('nmap_results.html', ip_address=ip_address, results=output)
    
@app.route('/nmap_output', methods=['GET'])
def nmap_output():
    try:
        with open('nmap_output.txt', 'r') as file:
            lines = file.readlines()
        
        # Remove extra spaces after each line
        formatted_lines = [line.strip() for line in lines]
    except FileNotFoundError:
        formatted_lines = ["Nmap output file not found."]

    return render_template('nmap_output.html', lines=formatted_lines)


async def fetch_for_forms(session, form_action, form_data):
    async with session.post(form_action, data=form_data) as response:
        response_time_start = time.time()
        response_content = await response.read()
        response_time_end = time.time()
        
        response_time = response_time_end - response_time_start
        response_length = len(response_content)
        return {
            'code': response.status,
            'time': response_time,
            'length': response_length,
            'input': form_data.get('searchFor', '')
        }

async def fetch_for_forms(session, url, data):
    start_time = asyncio.get_event_loop().time()
    async with session.post(url, data=data) as response:
        content = await response.text()
        end_time = asyncio.get_event_loop().time()
        return {
            'code': response.status,
            'length': len(content),
            'time': end_time - start_time,
            'input': data
        }

@app.route('/sql_injection', methods=['GET', 'POST'])
async def sql_injection():
    if request.method == 'POST':
        url = request.form['url']
        sort_by = request.form.get('sort_by', 'code')

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html_content = await response.text()

            soup = BeautifulSoup(html_content, 'html.parser')
            forms = soup.find_all('form')

            if not forms:
                return "No forms found on the page."

            results = []
            for form in forms:
                form_action = form.get('action', '')
                form_action = urljoin(url, form_action)
                
                form_data = {}
                for input_element in form.find_all(['input', 'textarea', 'select']):
                    name = input_element.get('name')
                    if name:
                        form_data[name] = input_element.get('value', '')

                async with aiofiles.open('sql_wordlist.txt', mode='r') as wordlist:
                    tasks = []
                    async for word in wordlist:
                        word = word.strip()
                        if word:
                            for field in form_data:
                                test_data = form_data.copy()
                                test_data[field] = word
                                tasks.append(fetch_for_forms(session, form_action, test_data))

                    form_results = await asyncio.gather(*tasks)
                    results.extend(form_results)

            # Sort results
            results.sort(key=lambda x: x[sort_by])

            # Save results to a file
            async with aiofiles.open('sql_injection_output.txt', mode='w') as file:
                for result in results:
                    await file.write(f"Code: {result['code']}, Response Time: {result['time']:.2f}, "
                                     f"Response Length: {result['length']}, Input: {result['input']}\n")

            return render_template('sql_injection_results.html', results=results)

async def fetch_for_forms(session, url, data):
    start_time = asyncio.get_event_loop().time()
    async with session.post(url, data=data) as response:
        end_time = asyncio.get_event_loop().time()
        response_time = end_time - start_time
        response_text = await response.text()
        return {
            'code': response.status,
            'time': response_time,
            'length': len(response_text),
            'input': data,
            'data': response_text
        }

@app.route('/xss_injection', methods=['GET', 'POST'])
async def xss_injection():
    if request.method == 'POST':
        url = request.form['url']
        sort_by = request.form.get('sort_by', 'code')

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html_content = await response.text()

            soup = BeautifulSoup(html_content, 'html.parser')
            forms = soup.find_all('form')

            if not forms:
                return "No forms found on the page."

            results = []
            for form in forms:
                form_action = form.get('action', '')
                form_action = urljoin(url, form_action)
                
                form_data = {}
                for input_element in form.find_all(['input', 'textarea', 'select']):
                    name = input_element.get('name')
                    if name:
                        form_data[name] = input_element.get('value', '')

                async with aiofiles.open('xss_wordlist.txt', mode='r') as wordlist:
                    tasks = []
                    async for word in wordlist:
                        word = word.strip()
                        if word:
                            for field in form_data:
                                test_data = form_data.copy()
                                test_data[field] = word
                                tasks.append(fetch_for_forms(session, form_action, test_data))

                    form_results = await asyncio.gather(*tasks)
                    results.extend(form_results)

            # Sort results
            results.sort(key=lambda x: x[sort_by])

            # Save results to a file
            async with aiofiles.open('xss_injection_output.txt', mode='w') as file:
                for result in results:
                    if "6969" in result['data']:
                        await file.write(f"Code: {result['code']}, Response Time: {result['time']:.2f}, "
                                         f"Response Length: {result['length']}, Input: {result['input']}\n")

            return render_template('xss_injection_results.html', results=results)

    return render_template('xss_injection.html')

@app.route('/xss_injection_output')
async def xss_injection_output():
    try:
        async with aiofiles.open('xss_injection_output.txt', mode='r') as file:
            output = await file.read()
    except FileNotFoundError:
        output = "xss_injection_output.txt not found."
    
    return render_template('xss_injection_output.html', file_content=output)


@app.route('/sql_injection_output')
async def sql_injection_output():
    try:
        async with aiofiles.open('sql_injection_output.txt', mode='r') as file:
            output = await file.read()
    except FileNotFoundError:
        output = "sql_injection_output.txt not found."
    
    return render_template('sql_injection_output.html', file_content=output)


if __name__ == '__main__':
    app.run(debug=True)
