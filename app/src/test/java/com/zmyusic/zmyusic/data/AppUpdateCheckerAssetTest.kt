package com.zmyusic.zmyusic.data

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class AppUpdateCheckerAssetTest {

    private fun asset(name: String) = ReleaseAsset(name, "https://example.test/$name")

    private val abis = listOf("arm64-v8a", "armeabi-v7a", "x86_64")

    @Test
    fun `phone takes its universal build and ignores tv and wear`() {
        val assets = listOf(
            asset("ZMyusic-1.0.0-android-tv-universal.apk"),
            asset("ZMyusic-1.0.0-android-wear.apk"),
            asset("ZMyusic-1.0.0-android-phone-arm64-v8a.apk"),
            asset("ZMyusic-1.0.0-android-phone-universal.apk"),
        )

        assertEquals(
            "https://example.test/ZMyusic-1.0.0-android-phone-universal.apk",
            pickApkAsset(assets, "phone", abis),
        )
    }

    @Test
    fun `phone falls back to its abi split`() {
        val assets = listOf(
            asset("ZMyusic-1.0.0-android-tv-arm64-v8a.apk"),
            asset("ZMyusic-1.0.0-android-phone-x86_64.apk"),
            asset("ZMyusic-1.0.0-android-phone-arm64-v8a.apk"),
        )

        assertEquals(
            "https://example.test/ZMyusic-1.0.0-android-phone-arm64-v8a.apk",
            pickApkAsset(assets, "phone", abis),
        )
    }

    @Test
    fun `tv takes the tv asset, never the phone one`() {
        val assets = listOf(
            asset("ZMyusic-1.0.0-android-phone-universal.apk"),
            asset("ZMyusic-1.0.0-android-tv-universal.apk"),
        )

        assertEquals(
            "https://example.test/ZMyusic-1.0.0-android-tv-universal.apk",
            pickApkAsset(assets, "tv", abis),
        )
    }

    @Test
    fun `legacy names still resolve for both apps`() {
        val legacy = listOf(
            asset("ZMyusic-v1.9.1.apk"),
            asset("ZMyusic-v1.9.1_arm64-v8a.apk"),
            asset("ZMyusicTV-v1.9.1.apk"),
            asset("ZMyusicTV-v1.9.1_arm64-v8a.apk"),
        )

        assertEquals("https://example.test/ZMyusic-v1.9.1.apk", pickApkAsset(legacy, "phone", abis))
        assertEquals("https://example.test/ZMyusicTV-v1.9.1.apk", pickApkAsset(legacy, "tv", abis))
    }

    @Test
    fun `legacy splits resolve by abi`() {
        val splits = listOf(
            asset("ZMyusic-v1.9.1_x86_64.apk"),
            asset("ZMyusic-v1.9.1_arm64-v8a.apk"),
            asset("ZMyusicTV-v1.9.1_x86_64.apk"),
            asset("ZMyusicTV-v1.9.1_arm64-v8a.apk"),
        )

        assertEquals(
            "https://example.test/ZMyusic-v1.9.1_arm64-v8a.apk",
            pickApkAsset(splits, "phone", abis),
        )
        assertEquals(
            "https://example.test/ZMyusicTV-v1.9.1_arm64-v8a.apk",
            pickApkAsset(splits, "tv", abis),
        )
    }

    @Test
    fun `no matching apk returns null`() {
        assertNull(pickApkAsset(listOf(asset("ZMyusic-1.0.0-android-wear.apk")), "phone", abis))
        assertNull(pickApkAsset(emptyList(), "tv", abis))
    }
}
