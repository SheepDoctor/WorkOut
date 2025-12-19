package com.example.workout

import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.FragmentContainerView
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.setupWithNavController
import com.google.android.material.bottomnavigation.BottomNavigationView

class MainActivity : AppCompatActivity() {
    companion object {
        private const val TAG = "MainActivity"
    }
    
    private var navigationSetup = false
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d(TAG, "onCreate: Starting MainActivity")
        
        try {
            setContentView(R.layout.activity_main)
            Log.d(TAG, "onCreate: Layout inflated successfully")
        } catch (e: Exception) {
            Log.e(TAG, "onCreate: Error occurred", e)
            throw e
        }
    }
    
    override fun onStart() {
        super.onStart()
        Log.d(TAG, "onStart")
        
        // Setup navigation in onStart when Fragment is guaranteed to be created
        if (!navigationSetup) {
            setupNavigation()
        }
    }
    
    private fun setupNavigation() {
        try {
            val navView: BottomNavigationView? = findViewById(R.id.nav_view)
            Log.d(TAG, "setupNavigation: navView = $navView")
            
            val navHostFragment = supportFragmentManager.findFragmentById(R.id.nav_host_fragment) as? NavHostFragment
            Log.d(TAG, "setupNavigation: navHostFragment = $navHostFragment")
            
            if (navHostFragment != null) {
                val navController = navHostFragment.navController
                Log.d(TAG, "setupNavigation: navController = $navController")
                
                navView?.setupWithNavController(navController)
                navigationSetup = true
                Log.d(TAG, "setupNavigation: Navigation setup completed")
            } else {
                Log.e(TAG, "setupNavigation: NavHostFragment not found!")
            }
        } catch (e: Exception) {
            Log.e(TAG, "setupNavigation: Error setting up navigation", e)
        }
    }
    
    override fun onResume() {
        super.onResume()
        Log.d(TAG, "onResume")
    }
    
    override fun onPause() {
        super.onPause()
        Log.d(TAG, "onPause")
    }
    
    override fun onStop() {
        super.onStop()
        Log.d(TAG, "onStop")
    }
    
    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "onDestroy")
    }
}

