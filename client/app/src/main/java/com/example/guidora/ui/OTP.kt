// OTPScreen.kt

package com.example.guidora.ui

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ColorFilter
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.guidora.R

// =================================================================
// تعاریف رنگ‌ها و ثابت‌ها
// =================================================================

val GuidoraBlue = Color(0xFF4396A5)
val HighlightGray = Color(0xFFE8E8E8)

// =================================================================
// صفحه اصلی OTPScreen
// =================================================================

@Composable
fun OTPScreen(
    onBackPressed: () -> Unit = {},
    // 💡 پارامتر ناوبری برای انتقال به RoleScreen
    onVerificationSuccess: () -> Unit
) {
    val logoSize = 300.dp
    val personIconSize = 70.dp

    val otpLength = 6
    val otpValues = remember {
        mutableStateListOf<TextFieldValue>().apply {
            repeat(otpLength) { add(TextFieldValue("")) }
        }
    }

    val focusRequesters = remember { List<FocusRequester>(otpLength) { FocusRequester() } }
    val focusManager = LocalFocusManager.current

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        containerColor = Color.White
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(horizontal = 32.dp, vertical = 48.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Top
        ) {
            // 1. لوگوی Guidora
            Box(
                modifier = Modifier
                    .size(logoSize)
                    .clip(CircleShape)
                    .background(GuidoraBlue.copy(alpha = 0f)),
                contentAlignment = Alignment.Center
            ) {
                Image(
                    painter = painterResource(id = R.drawable.uploaded_logo),
                    contentDescription = "Guidora Logo",
                    modifier = Modifier.fillMaxSize()
                )
            }

            Spacer(modifier = Modifier.height(10.dp))

            // 2. آیکون آدمک بین دو خط
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Divider(
                    color = Color.LightGray.copy(alpha = 0.5f),
                    modifier = Modifier.weight(1f).height(1.dp)
                )

                Image(
                    painter = painterResource(id = R.drawable.ic_person), // مطمئن شوید ic_person وجود دارد
                    contentDescription = "User Icon",
                    modifier = Modifier
                        .size(personIconSize)
                        .padding(horizontal = 8.dp),
                )

                Divider(
                    color = Color.LightGray.copy(alpha = 0.5f),
                    modifier = Modifier.weight(1f).height(1.dp)
                )
            }

            Spacer(modifier = Modifier.height(32.dp))

            // 3. عنوان
            Text(
                text = "کد ارسال شده را وارد کنید",
                fontSize = 18.sp,
                fontWeight = FontWeight.Normal,
                color = Color.Black
            )

            Spacer(modifier = Modifier.height(16.dp))

            // 4. فیلدهای OTP و هایلایت تیره
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(HighlightGray)
                    .padding(vertical = 8.dp, horizontal = 16.dp),
                horizontalArrangement = Arrangement.Start,
                verticalAlignment = Alignment.CenterVertically
            ) {

                // فیلدهای OTP
                Row(
                    horizontalArrangement = Arrangement.SpaceBetween,
                    modifier = Modifier.weight(1f)
                ) {
                    repeat(otpLength) { index ->
                        OtpTextField(
                            value = otpValues[index],
                            onValueChange = { newValue: TextFieldValue ->
                                // منطق فوکوس خودکار
                                if (newValue.text.length <= 1 && newValue.text.all { it.isDigit() }) {
                                    otpValues[index] = newValue

                                    if (newValue.text.isNotEmpty()) {
                                        if (index < otpLength - 1) {
                                            focusRequesters[index + 1].requestFocus()
                                        } else {
                                            focusManager.clearFocus()

                                            // 🚀 منطق انتقال به RoleScreen
                                            val isComplete = otpValues.all { it.text.isNotEmpty() }
                                            if (isComplete) {
                                                onVerificationSuccess()
                                            }
                                        }
                                    } else if (newValue.text.isEmpty()) {
                                        if (index > 0) {
                                            focusRequesters[index - 1].requestFocus()
                                        }
                                    }
                                }
                            },
                            focusRequester = focusRequesters[index]
                        )
                    }
                }

                Spacer(modifier = Modifier.width(8.dp))

                // آیکون کلید
                Image(
                    painter = painterResource(id = R.drawable.ic_key), // مطمئن شوید ic_key وجود دارد
                    contentDescription = "Key Icon",
                    modifier = Modifier
                        .size(24.dp)
                        .padding(start = 4.dp),
                    colorFilter = ColorFilter.tint(GuidoraBlue)
                )
            }

            Spacer(modifier = Modifier.height(32.dp))

            // 5. دکمه بازگشت
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { onBackPressed() },
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Start
            ) {
                // آیکون فلش بازگشت
                Image(
                    painter = painterResource(id = R.drawable.ic_back_arrow), // مطمئن شوید ic_back_arrow وجود دارد
                    contentDescription = "Back Arrow",
                    modifier = Modifier.size(20.dp),
                    colorFilter = ColorFilter.tint(GuidoraBlue)
                )

                Spacer(modifier = Modifier.width(8.dp))

                // متن بازگشت
                Text(
                    text = "بازگشت",
                    color = GuidoraBlue,
                    fontSize = 20.sp
                )
            }
        }
    }
}

@Composable
fun OtpTextField(
    value: TextFieldValue,
    onValueChange: (TextFieldValue) -> Unit,
    focusRequester: FocusRequester
) {
    var isFocused by remember { mutableStateOf(false) }

    BasicTextField(
        value = value,
        onValueChange = onValueChange,
        modifier = Modifier
            .width(40.dp)
            .height(64.dp)
            .focusRequester(focusRequester)
            .onFocusChanged { state ->
                isFocused = state.isFocused
            },

        textStyle = TextStyle(
            fontSize = 24.sp,
            textAlign = TextAlign.Center,
            fontWeight = FontWeight.Bold,
            color = Color.Black,
            lineHeight = 24.sp,
        ),
        keyboardOptions = KeyboardOptions(
            keyboardType = KeyboardType.Number,
            imeAction = ImeAction.Next
        ),
        singleLine = true,
        cursorBrush = SolidColor(GuidoraBlue),

        decorationBox = { innerTextField ->
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .clip(RoundedCornerShape(8.dp))
                    .background(Color.White)
                    .border(
                        width = 2.dp,
                        color = if (isFocused || value.text.isNotEmpty()) GuidoraBlue else Color.LightGray.copy(alpha = 0.8f),
                        shape = RoundedCornerShape(8.dp)
                    ),
                contentAlignment = Alignment.Center
            ) {
                innerTextField()
            }
        }
    )
}