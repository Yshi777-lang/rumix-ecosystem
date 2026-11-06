plugins { id("com.android.application") }
android {
    namespace = "com.termux.reborn"
    compileSdk = 34
    defaultConfig {
        applicationId = "com.termux.reborn"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
    }
    buildTypes { release { isMinifyEnabled = false } }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_11; targetCompatibility = JavaVersion.VERSION_11 }
}
