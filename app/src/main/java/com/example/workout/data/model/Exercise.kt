package com.example.workout.data.model

data class Exercise(
    val name: String,
    val steps: List<String>,
    val keyPoints: List<String>,
    val illustrationUrl: String = ""
)

