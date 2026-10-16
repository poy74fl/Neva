/**
 * Marlin 3D Printer Firmware
 * Copyright (c) 2020 MarlinFirmware [https://github.com/MarlinFirmware/Marlin]
 *
 * Based on Sprinter and grbl.
 * Copyright (c) 2011 Camiel Gubbels / Erik van der Zalm
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 */

//
// Main Menu
//

#include "../../inc/MarlinConfigPre.h"

#if HAS_MARLINUI_MENU

#include "menu_item.h"
#include "../../module/temperature.h"
#include "../../gcode/queue.h"
#include "../../module/printcounter.h"
#include "../../module/stepper.h"
#include "../../sd/cardreader.h"

#if ENABLED(FILAMENT_RUNOUT_SENSOR)
  #include "../../feature/runout.h"
#endif

#if ENABLED(PSU_CONTROL)
  #include "../../feature/power.h"
#endif

#if HAS_GAMES && DISABLED(LCD_INFO_MENU)
  #include "game/game.h"
#endif

#if ANY(HAS_MEDIA, HOST_PROMPT_SUPPORT) || defined(ACTION_ON_CANCEL)
  #define MACHINE_CAN_STOP 1
#endif
#if ANY(HAS_MEDIA, HOST_PROMPT_SUPPORT, PARK_HEAD_ON_PAUSE) || defined(ACTION_ON_PAUSE)
  #define MACHINE_CAN_PAUSE 1
#endif

#if ENABLED(MMU2_MENUS)
  #include "menu_mmu2.h"
#endif

#if ENABLED(PASSWORD_FEATURE)
  #include "../../feature/password/password.h"
#endif

#if (ENABLED(HOST_START_MENU_ITEM) && defined(ACTION_ON_START)) || (ENABLED(HOST_SHUTDOWN_MENU_ITEM) && defined(SHUTDOWN_ACTION))
  #include "../../feature/host_actions.h"
#endif

#if ENABLED(GCODE_REPEAT_MARKERS)
  #include "../../feature/repeat.h"
#endif

void menu_tune();
void menu_cancelobject();
void menu_motion();
void menu_temperature();
void menu_configuration();

#if HAS_POWER_MONITOR
  void menu_power_monitor();
#endif

#if ENABLED(MIXING_EXTRUDER)
  void menu_mixer();
#endif

#if ENABLED(ADVANCED_PAUSE_FEATURE)
  void menu_change_filament();
#endif

#if ENABLED(LCD_INFO_MENU)
  void menu_info();
#endif

#if ANY(LED_CONTROL_MENU, CASE_LIGHT_MENU)
  void menu_led();
#endif

#if HAS_CUTTER
  void menu_spindle_laser();
#endif

#if ENABLED(PREHEAT_SHORTCUT_MENU_ITEM)
  void menu_preheat_only();
#endif

#if HAS_MULTI_LANGUAGE
  void menu_language();
#endif

void neva_print_latest_file();   // defini dans menu_media.cpp

// Neva : ecran "Test courroies" (valeurs StallGuard moyennes de X, Y, Z affichees en direct)
#if ALL(CUSTOM_MENU_MAIN, TMC_DEBUG, MONITOR_DRIVER_STATUS, HAS_STALLGUARD, HAS_STATUS_MESSAGE) && defined(NEVA_TEST_COURROIES_GCODE)

  #define NEVA_BELT_SCREEN 1

  void neva_belt_read(uint16_t m[3], uint16_t &spread, uint16_t &n, bool &running, bool &reporting); // definis dans feature/tmc_util.cpp
  void neva_belt_begin();
  void neva_belt_end();

  void menu_neva_belts() {
    ui.defer_status_screen();                                  // pas de retour automatique a l'ecran d'info pendant le test
    if (ui.use_click()) { ui.defer_status_screen(false); neva_belt_end(); return ui.go_back(); }

    uint16_t m[3], spread, n;
    bool running, reporting;
    neva_belt_read(m, spread, n, running, reporting);
    static uint8_t redraws;                                    // diagnostic : compteur de rafraichissements de l'ecran
    ++redraws;

    char bx[12], by[12], bz[12], be[24];
    if (n) {
      sprintf_P(bx, PSTR("%u"), (unsigned)m[0]);
      sprintf_P(by, PSTR("%u"), (unsigned)m[1]);
      sprintf_P(bz, PSTR("%u"), (unsigned)m[2]);
      sprintf_P(be, PSTR("%u%% n%u r%u %c"), (unsigned)spread, (unsigned)n, (unsigned)(redraws % 100), reporting ? 'R' : '-');
    }
    else {
      strcpy_P(bx, PSTR("--")); strcpy_P(by, PSTR("--")); strcpy_P(bz, PSTR("--"));
      sprintf_P(be, PSTR("-- n0 r%u %c"), (unsigned)(redraws % 100), reporting ? 'R' : '-');
    }

    START_SCREEN();
    STATIC_ITEM_F((running ? F("COURROIES: EN COURS") : F("COURROIES: FINI")), SS_DEFAULT|SS_INVERT);
    STATIC_ITEM_F(F("X : "), SS_LEFT, bx);
    STATIC_ITEM_F(F("Y : "), SS_LEFT, by);
    STATIC_ITEM_F(F("Z : "), SS_LEFT, bz);
    STATIC_ITEM_F(F("E: "), SS_LEFT, be);
    END_SCREEN();

    ui.refresh(LCDVIEW_CALL_REDRAW_NEXT);                      // rafraichit l'ecran en continu
  }

#endif

#if ENABLED(CUSTOM_MENU_MAIN)

  void _lcd_custom_menu_main_gcode(FSTR_P const fstr) {
    // Neva : les tests qui extrudent (1ere couche, filament, spirale) ne demarrent pas sans filament charge
    #if ENABLED(FILAMENT_RUNOUT_SENSOR)
      // La calibration (M117 Calibration...) n'extrude pas : pas besoin de filament
      const bool neva_needs_filament = strncmp_P(FTOP(fstr), PSTR("M117 Calibration"), 16) != 0;
      if (neva_needs_filament && FilamentMonitorBase::enabled && (FilamentSensorBase::poll_runout_states() & _BV(0))) {
        ui.set_status(F("Charger le filament !"), 0);
        ui.completion_feedback(false);
        ui.return_to_status();
        return;
      }
    #endif
    queue.inject(fstr);
    TERN_(CUSTOM_MENU_MAIN_SCRIPT_AUDIBLE_FEEDBACK, ui.completion_feedback());
    TERN_(CUSTOM_MENU_MAIN_SCRIPT_RETURN, ui.return_to_status());
  }

  void custom_menus_main() {
    START_MENU();
    BACK_ITEM(MSG_MAIN_MENU);

    #define HAS_CUSTOM_ITEM_MAIN(N) (defined(MAIN_MENU_ITEM_##N##_DESC) && defined(MAIN_MENU_ITEM_##N##_GCODE))

    #ifdef CUSTOM_MENU_MAIN_SCRIPT_DONE
      #define _DONE_SCRIPT "\n" CUSTOM_MENU_MAIN_SCRIPT_DONE
    #else
      #define _DONE_SCRIPT ""
    #endif
    #define GCODE_LAMBDA_MAIN(N) []{ _lcd_custom_menu_main_gcode(F(MAIN_MENU_ITEM_##N##_GCODE _DONE_SCRIPT)); }
    #define _CUSTOM_ITEM_MAIN(N) ACTION_ITEM_F(F(MAIN_MENU_ITEM_##N##_DESC), GCODE_LAMBDA_MAIN(N));
    #define _CUSTOM_ITEM_MAIN_CONFIRM(N)          \
      SUBMENU_F(F(MAIN_MENU_ITEM_##N##_DESC), []{ \
          MenuItem_confirm::confirm_screen(       \
            GCODE_LAMBDA_MAIN(N), nullptr,        \
            F(MAIN_MENU_ITEM_##N##_DESC "?")      \
          );                                      \
        })

    #define CUSTOM_ITEM_MAIN(N) do{ \
      constexpr char c = MAIN_MENU_ITEM_##N##_GCODE[strlen(MAIN_MENU_ITEM_##N##_GCODE) - 1]; \
      static_assert(c != '\n' && c != '\r', "MAIN_MENU_ITEM_" STRINGIFY(N) "_GCODE cannot have a newline at the end. Please remove it."); \
      if (ENABLED(MAIN_MENU_ITEM_##N##_CONFIRM)) \
        _CUSTOM_ITEM_MAIN_CONFIRM(N); \
      else \
        _CUSTOM_ITEM_MAIN(N); \
    }while(0)

    #if HAS_CUSTOM_ITEM_MAIN(1)
      CUSTOM_ITEM_MAIN(1);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(2)
      CUSTOM_ITEM_MAIN(2);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(3)
      CUSTOM_ITEM_MAIN(3);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(4)
      CUSTOM_ITEM_MAIN(4);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(5)
      CUSTOM_ITEM_MAIN(5);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(6)
      CUSTOM_ITEM_MAIN(6);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(7)
      CUSTOM_ITEM_MAIN(7);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(8)
      CUSTOM_ITEM_MAIN(8);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(9)
      CUSTOM_ITEM_MAIN(9);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(10)
      CUSTOM_ITEM_MAIN(10);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(11)
      CUSTOM_ITEM_MAIN(11);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(12)
      CUSTOM_ITEM_MAIN(12);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(13)
      CUSTOM_ITEM_MAIN(13);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(14)
      CUSTOM_ITEM_MAIN(14);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(15)
      CUSTOM_ITEM_MAIN(15);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(16)
      CUSTOM_ITEM_MAIN(16);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(17)
      CUSTOM_ITEM_MAIN(17);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(18)
      CUSTOM_ITEM_MAIN(18);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(19)
      CUSTOM_ITEM_MAIN(19);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(20)
      CUSTOM_ITEM_MAIN(20);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(21)
      CUSTOM_ITEM_MAIN(21);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(22)
      CUSTOM_ITEM_MAIN(22);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(23)
      CUSTOM_ITEM_MAIN(23);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(24)
      CUSTOM_ITEM_MAIN(24);
    #endif
    #if HAS_CUSTOM_ITEM_MAIN(25)
      CUSTOM_ITEM_MAIN(25);
    #endif
    #ifdef NEVA_BELT_SCREEN
      SUBMENU_F(F("Test courroies"), []{
        MenuItem_confirm::confirm_screen(
          []{
            neva_belt_begin();
            queue.inject(F(NEVA_TEST_COURROIES_GCODE _DONE_SCRIPT));
            ui.goto_screen(menu_neva_belts);
          },
          nullptr,
          F("Test courroies?")
        );
      });
    #endif
    END_MENU();
  }

#endif // CUSTOM_MENU_MAIN

#if ENABLED(ADVANCED_PAUSE_FEATURE)
  // This menu item is last with an encoder. Otherwise, somewhere in the middle.
  #if E_STEPPERS == 1 && DISABLED(FILAMENT_LOAD_UNLOAD_GCODES)
    #define FILAMENT_CHANGE_ITEM() YESNO_ITEM(MSG_FILAMENTCHANGE, menu_change_filament, nullptr, \
                                    GET_TEXT_F(MSG_FILAMENTCHANGE), (const char *)nullptr, F("?"))
  #else
    #define FILAMENT_CHANGE_ITEM() SUBMENU(MSG_FILAMENTCHANGE, menu_change_filament)
  #endif
#endif

void menu_main() {
  const bool busy = printingIsActive();
  #if HAS_MEDIA
    const bool card_detected = card.isMounted(),
               card_open = card_detected && card.isFileOpen();
  #endif

  START_MENU();
  BACK_ITEM(MSG_INFO_SCREEN);                         // 1. Surveiller

  if (busy) {
    #if MACHINE_CAN_PAUSE
      ACTION_ITEM(MSG_PAUSE_PRINT, ui.pause_print);
    #endif
    #if MACHINE_CAN_STOP
      SUBMENU(MSG_STOP_PRINT, []{
        MenuItem_confirm::select_screen(
          GET_TEXT_F(MSG_BUTTON_STOP), GET_TEXT_F(MSG_BACK),
          ui.abort_print, nullptr,
          GET_TEXT_F(MSG_STOP_PRINT), (const char *)nullptr, F("?")
        );
      });
    #endif

    #if ENABLED(GCODE_REPEAT_MARKERS)
      if (repeat.is_active())
        ACTION_ITEM(MSG_END_LOOPS, repeat.cancel);
    #endif

    SUBMENU(MSG_TUNE, menu_tune);

    #if ENABLED(CANCEL_OBJECTS) && DISABLED(SLIM_LCD_MENUS)
      SUBMENU(MSG_CANCEL_OBJECT, []{ editable.int8 = -1; ui.goto_screen(menu_cancelobject); });
    #endif

    #if HAS_TEMPERATURE
      SUBMENU(MSG_TEMPERATURE, menu_temperature);
    #endif

    SUBMENU(MSG_CONFIGURATION, menu_configuration);
  }
  else {
    if (TERN0(MACHINE_CAN_PAUSE, printingIsPaused()))
      ACTION_ITEM(MSG_RESUME_PRINT, ui.resume_print);

    // 2. Prechauffage (menu Temperature renomme dans language_fr.h)
    #if HAS_TEMPERATURE
      SUBMENU(MSG_TEMPERATURE, menu_temperature);
    #endif

    // 3. Imprimer SD  /  4. Actualiser media
    #if HAS_MEDIA
      if (!card_open)
        ACTION_ITEM(MSG_MEDIA_MENU, []{                    // Neva : remonte la carte a chaque ouverture (plus besoin d'"Actualiser"),
          card.mount();                                     // lit la liste AVANT d'ouvrir le menu, puis reinitialise
          card.get_num_items();                             // l'ecran (bus SPI partage avec la SD)
          ui.reinit_lcd();
          ui.goto_screen(MEDIA_MENU_GATEWAY);
        });
      if (!card_open) ACTION_ITEM_F(F("Imprimer le dernier"), []{ neva_print_latest_file(); });   // Neva : fichier le plus recent de la racine
      GCODES_ITEM(MSG_CHANGE_MEDIA, F("M21"));              // M21 : actualiser / remonter la SD
    #endif

    // 5. Changer filament
    #if ENABLED(ADVANCED_PAUSE_FEATURE)
      FILAMENT_CHANGE_ITEM();
    #endif

    // 6. Configuration
    SUBMENU(MSG_CONFIGURATION, menu_configuration);

    // 7. Mouvement
    SUBMENU(MSG_MOTION, menu_motion);

    // 8. Lumiere
    #if ANY(LED_CONTROL_MENU, CASE_LIGHT_MENU)
      SUBMENU(MSG_LEDS, menu_led);
    #endif
  }

  // 9. Infos imprimante (version, carte, thermistances, statistiques)
  #if ENABLED(LCD_INFO_MENU)
    SUBMENU(MSG_INFO_MENU, menu_info);
  #endif

  // 10. Tests (scripts G-code integres : 1ere couche, filament) - voir Configuration_adv.h
  #if ENABLED(CUSTOM_MENU_MAIN)
    if (TERN1(CUSTOM_MENU_MAIN_ONLY_IDLE, !busy)) {
      #ifdef CUSTOM_MENU_MAIN_TITLE
        SUBMENU_F(F(CUSTOM_MENU_MAIN_TITLE), custom_menus_main);
      #else
        SUBMENU(MSG_CUSTOM_COMMANDS, custom_menus_main);
      #endif
    }
  #endif

  #if HAS_SERVICE_INTERVALS
    static auto _service_reset = [](const int index) {
      print_job_timer.resetServiceInterval(index);
      ui.completion_feedback();
      ui.reset_status();
      ui.return_to_status();
    };
    #if SERVICE_INTERVAL_1 > 0
      CONFIRM_ITEM_F(F(SERVICE_NAME_1),
        MSG_BUTTON_RESET, MSG_BUTTON_CANCEL,
        []{ _service_reset(1); }, nullptr,
        GET_TEXT_F(MSG_SERVICE_RESET), F(SERVICE_NAME_1), F("?")
      );
    #endif
    #if SERVICE_INTERVAL_2 > 0
      CONFIRM_ITEM_F(F(SERVICE_NAME_2),
        MSG_BUTTON_RESET, MSG_BUTTON_CANCEL,
        []{ _service_reset(2); }, nullptr,
        GET_TEXT_F(MSG_SERVICE_RESET), F(SERVICE_NAME_2), F("?")
      );
    #endif
    #if SERVICE_INTERVAL_3 > 0
      CONFIRM_ITEM_F(F(SERVICE_NAME_3),
        MSG_BUTTON_RESET, MSG_BUTTON_CANCEL,
        []{ _service_reset(3); }, nullptr,
        GET_TEXT_F(MSG_SERVICE_RESET), F(SERVICE_NAME_3), F("?")
      );
    #endif
  #endif

  #if HAS_GAMES && DISABLED(LCD_INFO_MENU)
    #if ENABLED(GAMES_EASTER_EGG)
      SKIP_ITEM();
      SKIP_ITEM();
      SKIP_ITEM();
    #endif
    // Game sub-menu or the individual game
    {
      SUBMENU(
        #if HAS_GAME_MENU
          MSG_GAMES, menu_game
        #elif ENABLED(MARLIN_BRICKOUT)
          MSG_BRICKOUT, brickout.enter_game
        #elif ENABLED(MARLIN_INVADERS)
          MSG_INVADERS, invaders.enter_game
        #elif ENABLED(MARLIN_SNAKE)
          MSG_SNAKE, snake.enter_game
        #elif ENABLED(MARLIN_MAZE)
          MSG_MAZE, maze.enter_game
        #endif
      );
    }
  #endif

  #if HAS_MULTI_LANGUAGE
    SUBMENU(LANGUAGE, menu_language);
  #endif

  #if ENABLED(HOST_SHUTDOWN_MENU_ITEM) && defined(SHUTDOWN_ACTION)
    SUBMENU(MSG_HOST_SHUTDOWN, []{
      MenuItem_confirm::select_screen(
        GET_TEXT_F(MSG_BUTTON_PROCEED), GET_TEXT_F(MSG_BUTTON_CANCEL),
        []{ ui.return_to_status(); hostui.shutdown(); }, nullptr,
        GET_TEXT_F(MSG_HOST_SHUTDOWN), (const char *)nullptr, F("?")
      );
    });
  #endif

  END_MENU();
}

#endif // HAS_MARLINUI_MENU
