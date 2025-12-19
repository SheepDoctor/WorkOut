package com.example.workout.data.model

import com.example.workout.data.model.Exercise

data class WorkoutNote(
    val id: String,
    val title: String,
    val exercises: List<Exercise>,
    val createdAt: Long
)

