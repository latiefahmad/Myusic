package com.music.myusic.data

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class AppUpdateCheckerAssetTest {

    private fun asset(name: String) = ReleaseAsset(name, "https://example.test/$name")

    private val abis = listOf("arm64-v8a", "armeabi-v7a", "x86_64")

    @Test
    fun `phone takes its universal build and ignores tv and wear`() {
        val assets = listOf(
            asset("Myusic-1.0.0-android-tv-universal.apk"),
            asset("Myusic-1.0.0-android-wear.apk"),
            asset("Myusic-1.0.0-android-phone-arm64-v8a.apk"),
            asset("Myusic-1.0.0-android-phone-universal.apk"),
        )

        assertEquals(
            "https://example.test/Myusic-1.0.0-android-phone-universal.apk",
            pickApkAsset(assets, "phone", abis),
        )
    }

    @Test
    fun `phone falls back to its abi split`() {
        val assets = listOf(
            asset("Myusic-1.0.0-android-tv-arm64-v8a.apk"),
            asset("Myusic-1.0.0-android-phone-x86_64.apk"),
            asset("Myusic-1.0.0-android-phone-arm64-v8a.apk"),
        )

        assertEquals(
            "https://example.test/Myusic-1.0.0-android-phone-arm64-v8a.apk",
            pickApkAsset(assets, "phone", abis),
        )
    }

    @Test
    fun `tv takes the tv asset, never the phone one`() {
        val assets = listOf(
            asset("Myusic-1.0.0-android-phone-universal.apk"),
            asset("Myusic-1.0.0-android-tv-universal.apk"),
        )

        assertEquals(
            "https://example.test/Myusic-1.0.0-android-tv-universal.apk",
            pickApkAsset(assets, "tv", abis),
        )
    }

    @Test
    fun `legacy names still resolve for both apps`() {
        val legacy = listOf(
            asset("Myusic-v1.9.1.apk"),
            asset("Myusic-v1.9.1_arm64-v8a.apk"),
            asset("MyusicTV-v1.9.1.apk"),
            asset("MyusicTV-v1.9.1_arm64-v8a.apk"),
        )

        assertEquals("https://example.test/Myusic-v1.9.1.apk", pickApkAsset(legacy, "phone", abis))
        assertEquals("https://example.test/MyusicTV-v1.9.1.apk", pickApkAsset(legacy, "tv", abis))
    }

    @Test
    fun `no matching apk returns null`() {
        assertNull(pickApkAsset(listOf(asset("Myusic-1.0.0-android-wear.apk")), "phone", abis))
        assertNull(pickApkAsset(emptyList(), "tv", abis))
    }
}
