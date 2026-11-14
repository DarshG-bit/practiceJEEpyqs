using System;
using System.IO;
using System.Windows;
using System.Windows.Input;
using Microsoft.Web.WebView2.Core;

namespace JEEPYQPractice
{
    public partial class MainWindow : Window
    {
        private bool _isFullScreen = false;
        private WindowStyle _previousStyle = WindowStyle.SingleBorderWindow;
        private WindowState _previousState = WindowState.Normal;

        public MainWindow()
        {
            InitializeComponent();
            Loaded += MainWindow_Loaded;
            KeyDown += MainWindow_KeyDown;
        }

        private async void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            try
            {
                // 1. Set persistent user data folder in LocalAppData
                string localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
                string userDataFolder = Path.Combine(localAppData, "JEEPYQPractice", "WebView2Profile");
                Directory.CreateDirectory(userDataFolder);

                // 2. Initialize CoreWebView2 Environment
                var env = await CoreWebView2Environment.CreateAsync(null, userDataFolder);
                await webView.EnsureCoreWebView2Async(env);

                // 3. Configure settings
                webView.CoreWebView2.Settings.IsStatusBarEnabled = false;
                webView.CoreWebView2.Settings.AreDevToolsEnabled = true;

                // 4. Locate content root directory (parent of windows-app or current directory)
                string contentDir = FindContentDirectory();

                // 5. Map local directory to secure virtual hostname https://app.local/
                webView.CoreWebView2.SetVirtualHostNameToFolderMapping(
                    "app.local",
                    contentDir,
                    CoreWebView2HostResourceAccessKind.Allow
                );

                // 6. Navigate to index.html under virtual secure host
                webView.CoreWebView2.Navigate("https://app.local/index.html");

                // 7. Hide loading overlay once page finishes loading
                webView.NavigationCompleted += (s, args) =>
                {
                    LoadingOverlay.Visibility = Visibility.Collapsed;
                };
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    "Error launching app:\n" + ex.Message,
                    "JEE PYQ Practice",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error
                );
            }
        }

        private string FindContentDirectory()
        {
            // First check if index.html is in parent directory (development mode)
            string currentDir = AppDomain.CurrentDomain.BaseDirectory;
            string parentDir = Path.GetFullPath(Path.Combine(currentDir, "..", "..", "..", ".."));
            if (File.Exists(Path.Combine(parentDir, "index.html")))
            {
                return parentDir;
            }

            // Check parent 1 level
            string oneUp = Path.GetFullPath(Path.Combine(currentDir, ".."));
            if (File.Exists(Path.Combine(oneUp, "index.html")))
            {
                return oneUp;
            }

            // Fallback to current base directory (production bundled mode)
            return currentDir;
        }

        private void MainWindow_KeyDown(object sender, KeyEventArgs e)
        {
            // F11: Toggle Fullscreen Exam Simulation Mode
            if (e.Key == Key.F11)
            {
                ToggleFullScreen();
                e.Handled = true;
            }
            // Escape exits fullscreen
            else if (e.Key == Key.Escape && _isFullScreen)
            {
                ToggleFullScreen();
                e.Handled = true;
            }
        }

        private void ToggleFullScreen()
        {
            if (!_isFullScreen)
            {
                _previousStyle = WindowStyle;
                _previousState = WindowState;
                WindowStyle = WindowStyle.None;
                WindowState = WindowState.Maximized;
                _isFullScreen = true;
            }
            else
            {
                WindowStyle = _previousStyle;
                WindowState = _previousState;
                _isFullScreen = false;
            }
        }
    }
}
