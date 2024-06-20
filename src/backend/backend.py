import os
import shutil
import subprocess
import tempfile
import uuid
import sys
import json

def list_angular_files(path):
    angular_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith((".component.ts", ".service.ts")):
                angular_files.append(os.path.join(root, file))
    return angular_files

def generate_angular_project():
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    npx_path = 'npx'  # or 'C:\\Program Files\\nodejs\\npx.cmd' if npx is not in PATH
    command = [npx_path, '@angular/cli', 'new', 'test-project', '--minimal']
    result = subprocess.run(command, check=True, shell=True, capture_output=True, encoding='utf-8', errors='replace')
    print(result.stdout)
    print(result.stderr)

    unique_id = str(uuid.uuid4())
    destination = os.path.join(temp_dir, f'test-project-{unique_id}')
    shutil.move(os.path.join(temp_dir, 'test-project'), destination)
    
    # Fix angular.json, create tsconfig.spec.json, and create karma.conf.js to ensure the project can be tested
    fix_angular_json(destination)
    create_tsconfig_spec(destination)
    create_karma_conf(destination)
    create_polyfills_ts(destination)  # Create polyfills.ts
    create_test_ts(destination)  # Create test.ts
    install_karma_dependencies(destination)
    
    return destination

def fix_angular_json(test_project_path):
    angular_json_path = os.path.join(test_project_path, 'angular.json')
    with open(angular_json_path, 'r') as file:
        angular_json = json.load(file)

    project_name = list(angular_json['projects'].keys())[0]
    angular_json['projects'][project_name]['architect']['test'] = {
        "builder": "@angular-devkit/build-angular:karma",
        "options": {
            "main": "src/test.ts",
            "polyfills": "src/polyfills.ts",
            "tsConfig": "tsconfig.spec.json",
            "karmaConfig": "karma.conf.js",
            "assets": [
                "src/favicon.ico",
                "src/assets"
            ],
            "styles": [
                "src/styles.css"
            ],
            "scripts": []
        }
    }

    with open(angular_json_path, 'w') as file:
        json.dump(angular_json, file, indent=2)

def create_tsconfig_spec(test_project_path):
    tsconfig_spec_content = {
        "extends": "./tsconfig.json",
        "compilerOptions": {
            "outDir": "./out-tsc/spec",
            "types": [
                "jasmine",
                "node"
            ]
        },
        "files": [
            "src/test.ts",
            "src/polyfills.ts"
        ],
        "include": [
            "src/**/*.spec.ts",
            "src/**/*.d.ts"
        ]
    }

    tsconfig_spec_path = os.path.join(test_project_path, 'tsconfig.spec.json')
    with open(tsconfig_spec_path, 'w') as file:
        json.dump(tsconfig_spec_content, file, indent=2)

def create_karma_conf(test_project_path):
    karma_conf_content = r"""
// Karma configuration file

module.exports = function (config) {
  config.set({
    basePath: '',
    frameworks: ['jasmine', '@angular-devkit/build-angular'],
    plugins: [
      require('karma-jasmine'),
      require('karma-chrome-launcher'),
      require('karma-jasmine-html-reporter'),
      require('karma-coverage'),
      require('@angular-devkit/build-angular/plugins/karma')
    ],
    client: {
      jasmine: {
        // you can add configuration options for Jasmine here
        // the possible options are listed at https://jasmine.github.io/api/edge/Configuration.html
        // for example, you can disable the random execution with `random: false`
        // or set a specific seed with `seed: 4321`
      },
      clearContext: false // leave Jasmine Spec Runner output visible in browser
    },
    jasmineHtmlReporter: {
      suppressAll: true // removes the duplicated traces
    },
    coverageReporter: {
      dir: require('path').join(__dirname, './coverage/test-project'),
      subdir: '.',
      reporters: [
        { type: 'html' },
        { type: 'text-summary' }
      ]
    },
    reporters: ['progress', 'kjhtml'],
    port: 9876,
    colors: true,
    logLevel: config.LOG_INFO,
    autoWatch: true,
    browsers: ['Chrome'],
    singleRun: false,
    restartOnFileChange: true
  });
};
"""
    karma_conf_path = os.path.join(test_project_path, 'karma.conf.js')
    with open(karma_conf_path, 'w') as file:
        file.write(karma_conf_content)
    
    print(f"karma.conf.js created at {karma_conf_path}")

def install_karma_dependencies(test_project_path):
    # Install karma dependencies
    karma_dependencies = [
        'karma',
        'karma-chrome-launcher',
        'karma-coverage',
        'karma-jasmine',
        'karma-jasmine-html-reporter',
        '@types/jasmine',
        '@types/node'
    ]
    subprocess.run(['npm', 'install', '--save-dev'] + karma_dependencies, cwd=test_project_path, check=True, shell=True)

def create_polyfills_ts(test_project_path):
    polyfills_ts_content = """
/**
 * This file includes polyfills needed by Angular and is loaded before the app.
 * You can add your own extra polyfills to this file.
 *
 * This file is divided into 2 sections:
 *   1. Browser polyfills. These are applied before loading ZoneJS and are sorted by browsers.
 *   2. Application imports. Files imported after ZoneJS that should be loaded before your main
 *      file.
 *
 * The current setup is for so-called "evergreen" browsers; the last versions of browsers that
 * automatically update themselves. This includes recent versions of Safari, Chrome (including
 * Opera), Edge on the desktop, and iOS and Android.
 *
 * Learn more in https://angular.io/guide/browser-support
 */

/***************************************************************************************************
 * BROWSER POLYFILLS
 */

/**
 * IE11 requires the following for NgClass support on SVG elements
 */
// import 'classlist.js';  // Run `npm install --save classlist.js`.

/**
 * Web Animations `@angular/platform-browser/animations`
 * Only required if AnimationBuilder is used within the application and using IE/Edge or Safari.
 * Standard animation support in Angular DOES NOT require any polyfills (as of Angular 6.0).
 */
// import 'web-animations-js';  // Run `npm install --save web-animations-js`.

/**
 * Zone JS is required by default for Angular itself.
 */
import 'zone.js';  // Included with Angular CLI.

/***************************************************************************************************
 * APPLICATION IMPORTS
 */
"""
    polyfills_ts_path = os.path.join(test_project_path, 'src', 'polyfills.ts')
    with open(polyfills_ts_path, 'w') as file:
        file.write(polyfills_ts_content)

def create_test_ts(test_project_path):
    test_ts_content = r"""
import 'zone.js/testing';
import { getTestBed } from '@angular/core/testing';
import {
  BrowserDynamicTestingModule,
  platformBrowserDynamicTesting
} from '@angular/platform-browser-dynamic/testing';

declare const require: any;

// First, initialize the Angular testing environment.
getTestBed().initTestEnvironment(
  BrowserDynamicTestingModule,
  platformBrowserDynamicTesting()
);
// Then we find all the tests.
const context = require.context('./', true, /\.spec\.ts$/);
// And load the modules.
context.keys().map(context);
"""
    test_ts_path = os.path.join(test_project_path, 'src', 'test.ts')
    with open(test_ts_path, 'w') as file:
        file.write(test_ts_content)
    test_ts_content = r"""
import 'zone.js/testing';
import { getTestBed } from '@angular/core/testing';
import {
  BrowserDynamicTestingModule,
  platformBrowserDynamicTesting
} from '@angular/platform-browser-dynamic/testing';

declare const require: {
  context(path: string, deep?: boolean, filter?: RegExp): {
    keys(): string[];
    <T>(id: string): T;
  };
};

// First, initialize the Angular testing environment.
getTestBed().initTestEnvironment(
  BrowserDynamicTestingModule,
  platformBrowserDynamicTesting()
);
// Then we find all the tests.
const context = require.context('./', true, /\.spec\.ts$/);
// And load the modules.
context.keys().map(context);
"""
    test_ts_path = os.path.join(test_project_path, 'src', 'test.ts')
    with open(test_ts_path, 'w') as file:
        file.write(test_ts_content)

def fix_file_structure(test_project_path):
    app_path = os.path.join(test_project_path, 'src', 'app')
    nested_app_path = os.path.join(app_path, 'src', 'app')

    if os.path.exists(nested_app_path):
        for item in os.listdir(nested_app_path):
            src_item_path = os.path.join(nested_app_path, item)
            dest_item_path = os.path.join(app_path, item)
            try:
                if os.path.exists(dest_item_path):
                    os.remove(dest_item_path)  # Remove the existing file
                shutil.move(src_item_path, app_path)
            except Exception as e:
                print(f"Error moving {src_item_path} to {app_path}: {e}")
        shutil.rmtree(os.path.join(app_path, 'src'))

    app_path = os.path.join(test_project_path, 'src', 'app')
    nested_app_path = os.path.join(app_path, 'src', 'app')

    if os.path.exists(nested_app_path):
        for item in os.listdir(nested_app_path):
            shutil.move(os.path.join(nested_app_path, item), app_path)
        shutil.rmtree(os.path.join(app_path, 'src'))

def copy_selected_files(project_path, selected_files, test_project_path):
    app_path = os.path.join(test_project_path, 'src', 'app')
    for file in selected_files:
        if file and os.path.exists(file):  # Check file exists
            relative_path = os.path.relpath(file, project_path)
            destination = os.path.join(app_path, relative_path)
            destination_dir = os.path.dirname(destination)
            try:
                if not os.path.exists(destination_dir):
                    os.makedirs(destination_dir)  # Create destination directory if it does not exist
                print(f"Copying {file} to {destination}")  # Debug information
                shutil.copy(file, destination)

                # Copy associated HTML and SCSS files if they exist
                base_name = os.path.splitext(file)[0]
                for extension in ['.html', '.scss']:
                    associated_file = base_name + extension
                    if os.path.exists(associated_file):
                        associated_destination = os.path.join(destination_dir, os.path.basename(associated_file))
                        print(f"Copying {associated_file} to {associated_destination}")  # Debug information
                        shutil.copy(associated_file, associated_destination)

            except FileNotFoundError as e:
                print(f"Error: {e}")
        else:
            print(f"Invalid file path received: {file}")  # Debug information
    app_path = os.path.join(test_project_path, 'src', 'app')
    for file in selected_files:
        if file and os.path.exists(file):  # Check file exists
            relative_path = os.path.relpath(file, project_path)
            destination = os.path.join(app_path, relative_path)
            destination_dir = os.path.dirname(destination)
            try:
                if not os.path.exists(destination_dir):
                    os.makedirs(destination_dir)  # Create destination directory if it does not exist
                print(f"Copying {file} to {destination}")  # Debug information
                shutil.copy(file, destination)
            except FileNotFoundError as e:
                print(f"Error: {e}")
        else:
            print(f"Invalid file path received: {file}")  # Debug information

def install_dependencies(test_project_path):
    subprocess.run(['npm', 'install'], cwd=test_project_path, check=True, shell=True)
    subprocess.run(['npm', 'install', '--save-dev', '@types/jasmine'], cwd=test_project_path, check=True, shell=True)

def setup_tests(selected_files, test_project_path):
    app_path = os.path.join(test_project_path, 'src', 'app')
    for file in selected_files:
        file_name = os.path.basename(file)
        test_file_content = None
        if "component" in file_name:
            test_file_content = f"""
import {{ ComponentFixture, TestBed }} from '@angular/core/testing';
import {{ {file_name.split('.')[0]} }} from './{file_name.split('.')[0]}';

describe('{file_name.split('.')[0]}', () => {{
  let component: {file_name.split('.')[0]};
  let fixture: ComponentFixture<{file_name.split('.')[0]}>;

  beforeEach(async () => {{
    await TestBed.configureTestingModule({{
      declarations: [ {file_name.split('.')[0]} ]
    }})
    .compileComponents();
  }});

  beforeEach(() => {{
    fixture = TestBed.createComponent({file_name.split('.')[0]});
    component = fixture.componentInstance;
    fixture.detectChanges();
  }});

  it('should create', () => {{
    expect(component).toBeTruthy();
  }});
}});
"""
        elif "service" in file_name:
            test_file_content = f"""
import {{ TestBed }} from '@angular/core/testing';
import {{ {file_name.split('.')[0]} }} from './{file_name.split('.')[0]}';

describe('{file_name.split('.')[0]}', () => {{
  let service: {file_name.split('.')[0]};

  beforeEach(() => {{
    TestBed.configureTestingModule({{}});
    service = TestBed.inject({file_name.split('.')[0]});
  }});

  it('should be created', () => {{
    expect(service).toBeTruthy();
  }});
}});
"""
        if test_file_content:
            test_file_path = os.path.join(app_path, file_name.replace(".ts", ".spec.ts"))
            with open(test_file_path, "w") as test_file:
                test_file.write(test_file_content)

def main():
    if len(sys.argv) < 2:
        print("Usage: python backend.py <project_path> [selected_files]")
        sys.exit(1)

    command = sys.argv[1]
    
    if command == "list":
        project_path = sys.argv[2]
        angular_files = list_angular_files(project_path)
        print(json.dumps(angular_files))
    
    elif command == "generate":
        project_path = sys.argv[2]
        selected_files = sys.argv[3:]

        test_project_path = generate_angular_project()
        copy_selected_files(project_path, selected_files, test_project_path)
        fix_file_structure(test_project_path)
        install_dependencies(test_project_path)
        setup_tests(selected_files, test_project_path)
        print(f"The test project has been set up at: {test_project_path}")

if __name__ == "__main__":
    main()
